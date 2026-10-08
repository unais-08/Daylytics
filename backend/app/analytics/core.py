"""Compatibility dispatcher for the pure analytics functions."""

from typing import Any

import pandas as pd

from app.analytics.deep_work import deep_work
from app.analytics.focus import focus
from app.analytics.productivity import productivity
from app.analytics.sleep import sleep_focus
from app.analytics.sufficiency import data_sufficiency
from app.analytics.time_leaks import time_leaks
from app.analytics.trends import trends
from app.analytics.weekday_weekend import weekday_weekend


def career_output(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {"total_units": 0, "by_type": {}}
    return {
        "total_units": int(df["count"].sum()),
        "by_type": {
            str(k): int(v) for k, v in df.groupby("type")["count"].sum().items()
        },
    }


def overview(
    sessions: pd.DataFrame,
    distractions: pd.DataFrame,
    career: pd.DataFrame,
) -> dict[str, Any]:
    return {
        "deep_work_minutes": deep_work(sessions)["total_minutes"],
        "distraction_minutes": time_leaks(distractions)["total_minutes"],
        "career_units": career_output(career)["total_units"],
    }


def analyze(
    kind: str,
    sessions: pd.DataFrame,
    distractions: pd.DataFrame,
    sleep: pd.DataFrame,
    career: pd.DataFrame,
) -> dict[str, Any]:
    frames = [
        frame
        for frame in (sessions, distractions, sleep, career)
        if not frame.empty
    ]
    days = len(set(pd.concat(frames)["local_date"])) if frames else 0
    envelope = {"analysis": kind, "data_sufficiency": data_sufficiency(days)}
    results = {
        "time-leaks": lambda: time_leaks(distractions),
        "deep-work": lambda: deep_work(sessions),
        "best-worst-days": lambda: productivity(sessions, distractions, career),
        "focus-by-time": lambda: focus(sessions),
        "career-output": lambda: career_output(career),
        "weekday-weekend": lambda: weekday_weekend(sessions, distractions),
        "sleep-focus": lambda: sleep_focus(sessions, sleep),
        "trends": lambda: trends(sessions, distractions),
        "overview": lambda: overview(sessions, distractions, career),
    }
    envelope["result"] = results[kind]() if kind in results else results["overview"]()
    return envelope
