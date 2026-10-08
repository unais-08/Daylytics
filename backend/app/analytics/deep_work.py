"""Pure deep work analysis functions."""

from typing import Any

import pandas as pd


def deep_work(df: pd.DataFrame) -> dict[str, Any]:
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
