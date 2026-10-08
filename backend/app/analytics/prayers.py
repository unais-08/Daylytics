"""Pure prayers analysis functions."""

from typing import Any

import pandas as pd


def prayers(df: pd.DataFrame) -> dict[str, Any]:
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
