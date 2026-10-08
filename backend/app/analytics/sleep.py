"""Pure sleep analysis functions."""

from typing import Any

import pandas as pd


def sleep_focus(sessions: pd.DataFrame, sleep: pd.DataFrame) -> dict[str, Any]:
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
