"""Pure weekday weekend analysis functions."""

from typing import Any

import pandas as pd


def weekday_weekend(
    sessions: pd.DataFrame, distractions: pd.DataFrame
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
        result[label] = {
            "deep_work_minutes": round(
                float(work.loc[work["deep_work"] == True, "minutes"].sum()), 2
            ),
            "distraction_minutes": round(float(leak["minutes"].sum()), 2),
        }
    return result
