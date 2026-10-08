"""Pure focus analysis functions."""

from typing import Any

import pandas as pd


def focus(df: pd.DataFrame) -> dict[str, Any]:
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
