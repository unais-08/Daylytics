"""Pure time leaks analysis functions."""

from typing import Any

import pandas as pd


def time_leaks(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {"total_minutes": 0, "by_category": {}, "top_category": None}
    grouped = df.groupby("category")["minutes"].sum().sort_values(ascending=False)
    return {
        "total_minutes": round(float(df["minutes"].sum()), 2),
        "by_category": {str(k): round(float(v), 2) for k, v in grouped.items()},
        "top_category": str(grouped.index[0]) if len(grouped) else None,
    }
