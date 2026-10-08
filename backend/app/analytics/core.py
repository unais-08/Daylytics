from __future__ import annotations

from typing import Any

import pandas as pd

from app.config import get_settings


def data_sufficiency(days: int) -> dict[str, Any]:
    if days < 7:
        level, message = "insufficient", "Not enough data yet."
    elif days < 14:
        level, message = "early", "Early pattern, treat cautiously."
    elif days < 28:
        level, message = "preliminary", "Preliminary pattern."
    elif days < 90:
        level, message = "baseline", "Useful personal baseline."
    else:
        level, message = (
            "strong",
            "Enough historical data for more serious experiments.",
        )
    return {"days_with_data": days, "level": level, "message": message}


def _empty(kind: str) -> dict[str, Any]:
    return {"analysis": kind, "result": None}


def analyze(
    kind: str,
    sessions: pd.DataFrame,
    distractions: pd.DataFrame,
    prayers: pd.DataFrame,
    sleep: pd.DataFrame,
    career: pd.DataFrame,
) -> dict[str, Any]:
    frames = [
        frame
        for frame in (sessions, distractions, prayers, sleep, career)
        if not frame.empty
    ]
    days = len(set(pd.concat(frames)["local_date"])) if frames else 0
    envelope = {"analysis": kind, "data_sufficiency": data_sufficiency(days)}
    if kind == "time-leaks":
        result = _time_leaks(distractions)
    elif kind == "deep-work":
        result = _deep_work(sessions)
    elif kind == "best-worst-days":
        result = _productivity(sessions, distractions, career)
    elif kind == "focus-by-time":
        result = _focus(sessions)
    elif kind == "prayers":
        result = _prayers(prayers)
    elif kind == "career-output":
        result = _career(career)
    elif kind == "weekday-weekend":
        result = _weekday_weekend(sessions, distractions, prayers)
    elif kind == "sleep-focus":
        result = _sleep_focus(sessions, sleep)
    elif kind == "trends":
        result = _trends(sessions, distractions, prayers)
    else:
        result = _overview(sessions, distractions, prayers, career)
    envelope["result"] = result
    return envelope


def _time_leaks(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {"total_minutes": 0, "by_category": {}, "top_category": None}
    grouped = df.groupby("category")["minutes"].sum().sort_values(ascending=False)
    return {
        "total_minutes": round(float(df["minutes"].sum()), 2),
        "by_category": {str(k): round(float(v), 2) for k, v in grouped.items()},
        "top_category": str(grouped.index[0]) if len(grouped) else None,
    }


def _deep_work(df: pd.DataFrame) -> dict[str, Any]:
    deep = df[df["deep_work"] == True] if not df.empty else df
    if deep.empty:
        return {"total_minutes": 0, "session_count": 0, "average_focus": None}
    daily = deep.groupby("local_date")["minutes"].sum()
    return {
        "total_minutes": round(float(deep["minutes"].sum()), 2),
        "session_count": len(deep),
        "mean_daily_minutes": round(float(daily.mean()), 2),
        "median_daily_minutes": round(float(daily.median()), 2),
        "average_session_minutes": round(float(deep["minutes"].mean()), 2),
        "longest_session_minutes": round(float(deep["minutes"].max()), 2),
        "average_focus": round(float(deep["focus"].dropna().mean()), 2)
        if deep["focus"].notna().any()
        else None,
    }


def _productivity(
    sessions: pd.DataFrame, distractions: pd.DataFrame, career: pd.DataFrame
) -> dict[str, Any]:
    if sessions.empty and distractions.empty and career.empty:
        return {"days": [], "top_3": [], "bottom_3": []}
    dates = set()
    for frame in (sessions, distractions, career):
        if not frame.empty:
            dates.update(frame["local_date"])
    settings = get_settings()
    rows = []
    for day in sorted(dates):
        work = sessions[sessions["local_date"] == day]
        leak = distractions[distractions["local_date"] == day]
        output = career[career["local_date"] == day]
        deep = float(work.loc[work["deep_work"] == True, "minutes"].sum())
        focus = (
            float(work["focus"].dropna().mean()) if work["focus"].notna().any() else 0
        )
        units = float(output["count"].sum())
        distraction = float(leak["minutes"].sum())
        score = 100 * (
            0.45 * min(deep / settings.daily_deep_target_min, 1)
            + 0.2 * focus / 5
            + 0.2 * min(units / settings.daily_career_target_units, 1)
            + 0.15 * (1 - min(distraction / settings.daily_distraction_cap_min, 1))
        )
        rows.append({"date": str(day), "score": round(score, 2)})
    return {
        "days": rows,
        "top_3": sorted(rows, key=lambda x: x["score"], reverse=True)[:3],
        "bottom_3": sorted(rows, key=lambda x: x["score"])[:3],
    }


def _focus(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty or not df["focus"].notna().any():
        return {"by_hour": {}, "by_period": {}}
    valid = df[df["focus"].notna()].copy()
    by_hour = valid.groupby("hour")["focus"].agg(["mean", "count"])
    by_hour = by_hour[by_hour["count"] >= 3]
    period = pd.cut(
        valid["hour"], [-1, 11, 16, 24], labels=["morning", "afternoon", "evening"]
    )
    return {
        "by_hour": {
            str(int(k)): round(float(v), 2) for k, v in by_hour["mean"].items()
        },
        "by_period": {
            str(k): round(float(v), 2)
            for k, v in valid.groupby(period, observed=True)["focus"].mean().items()
        },
    }


def _prayers(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {
            "completed": 0,
            "missed": 0,
            "completion_percent": None,
            "by_prayer": {},
        }
    completed = int((df["status"] == "completed").sum())
    missed = int((df["status"] == "missed").sum())
    return {
        "completed": completed,
        "missed": missed,
        "completion_percent": round(100 * completed / len(df), 2),
        "by_prayer": {
            str(k): round(float((v == "completed").mean() * 100), 2)
            for k, v in df.groupby("prayer")["status"]
        },
    }


def _career(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {"total_units": 0, "by_type": {}}
    return {
        "total_units": int(df["count"].sum()),
        "by_type": {
            str(k): int(v) for k, v in df.groupby("type")["count"].sum().items()
        },
    }


def _weekday_weekend(
    sessions: pd.DataFrame, distractions: pd.DataFrame, prayers: pd.DataFrame
) -> dict[str, Any]:
    result = {}
    for label, day_filter in (
        ("weekday", lambda s: s < 5),
        ("weekend", lambda s: s >= 5),
    ):
        work = (
            sessions[day_filter(sessions["weekday"])]
            if not sessions.empty
            else sessions
        )
        leak = (
            distractions[day_filter(distractions["weekday"])]
            if not distractions.empty
            else distractions
        )
        pray = prayers[day_filter(prayers["weekday"])] if not prayers.empty else prayers
        result[label] = {
            "deep_work_minutes": round(
                float(work.loc[work["deep_work"] == True, "minutes"].sum()), 2
            ),
            "distraction_minutes": round(float(leak["minutes"].sum()), 2),
            "prayer_completion_percent": round(
                float((pray["status"] == "completed").mean() * 100), 2
            )
            if not pray.empty
            else None,
        }
    return result


def _sleep_focus(sessions: pd.DataFrame, sleep: pd.DataFrame) -> dict[str, Any]:
    if sessions.empty or sleep.empty:
        return {"correlation": None, "label": "correlation, not causation"}
    joined = sessions.merge(
        sleep, left_on="local_date", right_on="next_day", how="inner"
    )
    return {
        "correlation": round(float(joined["sleep_minutes"].corr(joined["focus"])), 3)
        if len(joined) > 1
        else None,
        "label": "correlation, not causation",
    }


def _trends(
    sessions: pd.DataFrame, distractions: pd.DataFrame, prayers: pd.DataFrame
) -> dict[str, Any]:
    if sessions.empty:
        return {"daily_deep_work": [], "weekly_distraction": [], "weekly_prayer": []}
    daily = (
        sessions[sessions["deep_work"] == True].groupby("local_date")["minutes"].sum()
    )
    return {
        "daily_deep_work": [
            {"date": str(k), "minutes": round(float(v), 2)} for k, v in daily.items()
        ],
        "weekly_distraction": [],
        "weekly_prayer": [],
    }


def _overview(
    sessions: pd.DataFrame,
    distractions: pd.DataFrame,
    prayers: pd.DataFrame,
    career: pd.DataFrame,
) -> dict[str, Any]:
    return {
        "deep_work_minutes": _deep_work(sessions)["total_minutes"],
        "distraction_minutes": _time_leaks(distractions)["total_minutes"],
        "career_units": _career(career)["total_units"],
        "prayer_completion_percent": _prayers(prayers)["completion_percent"],
    }
