"""UTC and configured-local-time helpers shared across application layers."""

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from app.core.config import get_settings


def utc_now() -> datetime:
    return datetime.now(UTC)


def duration_minutes(start: datetime, end: datetime | None) -> float | None:
    if end is None:
        return None
    if start.tzinfo is None and end.tzinfo is not None:
        start = start.replace(tzinfo=end.tzinfo)
    elif end.tzinfo is None and start.tzinfo is not None:
        end = end.replace(tzinfo=start.tzinfo)
    return round((end - start).total_seconds() / 60, 2)


def comparable_utc(value: datetime) -> datetime:
    return (value if value.tzinfo else value.replace(tzinfo=UTC)).astimezone(UTC)


def local_date(value: datetime) -> datetime.date:
    return comparable_utc(value).astimezone(ZoneInfo(get_settings().timezone)).date()
