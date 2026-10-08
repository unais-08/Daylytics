"""Pure productivity analysis functions."""

from typing import Any

import pandas as pd

from app.core.config import get_settings


def productivity(
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
