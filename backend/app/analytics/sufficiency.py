"""Pure sufficiency analysis functions."""

from typing import Any


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
