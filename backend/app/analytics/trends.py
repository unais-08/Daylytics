"""Pure trends analysis functions."""

from typing import Any

import pandas as pd


def trends(
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
