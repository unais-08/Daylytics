"""Load analytics records, validate filters, and invoke pure analysis functions."""

from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics import analyze
from app.analytics.frames import build_frame
from app.core.config import get_settings
from app.core.exceptions import InvalidParameterError
from app.core.time import duration_minutes
from app.models import CareerOutput, Distraction, PrayerLog, SleepLog, WorkSession

ALLOWED_ANALYSES = {
    "time-leaks",
    "deep-work",
    "best-worst-days",
    "focus-by-time",
    "prayers",
    "career-output",
    "weekday-weekend",
    "sleep-focus",
    "trends",
    "overview",
}
ALLOWED_RANGES = ["today", "7d", "30d", "custom"]


def _local_datetime(value: datetime, zone: ZoneInfo) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(zone)


def _in_range(day: date, start_date: date | None, end_date: date | None) -> bool:
    return (start_date is None or day >= start_date) and (
        end_date is None or day <= end_date
    )


def _load_frames(
    db: Session, start_date: date | None, end_date: date | None
):
    zone = ZoneInfo(get_settings().timezone)
    sessions = []
    for item in db.scalars(select(WorkSession)).all():
        local = _local_datetime(item.start_time, zone)
        if _in_range(local.date(), start_date, end_date) and item.end_time is not None:
            sessions.append(
                {
                    "local_date": local.date(),
                    "weekday": local.weekday(),
                    "hour": local.hour,
                    "minutes": duration_minutes(item.start_time, item.end_time) or 0,
                    "deep_work": bool(item.deep_work),
                    "focus": item.focus_score,
                }
            )
    distractions = []
    for item in db.scalars(select(Distraction)).all():
        local = _local_datetime(item.start_time, zone)
        if (
            _in_range(local.date(), start_date, end_date)
            and item.end_time is not None
        ):
            distractions.append(
                {
                    "local_date": local.date(),
                    "weekday": local.weekday(),
                    "minutes": duration_minutes(item.start_time, item.end_time) or 0,
                    "category": item.category.value,
                }
            )
    prayers = [
        {
            "local_date": item.date,
            "weekday": item.date.weekday(),
            "prayer": item.prayer.value,
            "status": item.status.value,
        }
        for item in db.scalars(select(PrayerLog)).all()
        if _in_range(item.date, start_date, end_date)
    ]
    sleep = []
    for item in db.scalars(select(SleepLog)).all():
        wake = _local_datetime(item.wake_time, zone)
        if _in_range(wake.date(), start_date, end_date):
            sleep.append(
                {
                    "local_date": wake.date(),
                    "next_day": wake.date() + timedelta(days=1),
                    "sleep_minutes": duration_minutes(item.sleep_start, item.wake_time)
                    or 0,
                }
            )
    career = []
    for item in db.scalars(select(CareerOutput)).all():
        local = _local_datetime(item.logged_at, zone)
        if _in_range(local.date(), start_date, end_date):
            career.append(
                {
                    "local_date": local.date(),
                    "count": item.count,
                    "type": item.type.value,
                }
            )
    return (
        build_frame(
            sessions,
            ["local_date", "weekday", "hour", "minutes", "deep_work", "focus"],
        ),
        build_frame(distractions, ["local_date", "weekday", "minutes", "category"]),
        build_frame(prayers, ["local_date", "weekday", "prayer", "status"]),
        build_frame(sleep, ["local_date", "next_day", "sleep_minutes"]),
        build_frame(career, ["local_date", "count", "type"]),
    )


def analyze_request(
    db: Session,
    kind: str,
    range_name: str,
    start_date: date | None,
    end_date: date | None,
) -> dict:
    today_date = datetime.now(ZoneInfo(get_settings().timezone)).date()
    if range_name in {"today", "7d", "30d"}:
        days = {"today": 0, "7d": 6, "30d": 29}[range_name]
        start_date = today_date - timedelta(days=days)
        end_date = today_date
    elif range_name != "custom":
        raise InvalidParameterError(
            "INVALID_FILTER", details={"allowed_ranges": ALLOWED_RANGES}
        )
    if range_name == "custom" and (start_date is None or end_date is None):
        raise InvalidParameterError(
            "INVALID_DATE_RANGE",
            "Custom analytics ranges require both start_date and end_date.",
        )
    if start_date and end_date and end_date < start_date:
        raise InvalidParameterError("INVALID_DATE_RANGE")
    if start_date and end_date and (end_date - start_date).days > 366:
        raise InvalidParameterError("RANGE_TOO_LARGE")
    if kind not in ALLOWED_ANALYSES:
        raise InvalidParameterError(
            "INVALID_ANALYSIS_NAME",
            details={"allowed_names": sorted(ALLOWED_ANALYSES)},
        )
    result = analyze(kind, *_load_frames(db, start_date, end_date))
    result["range"] = {
        "start_date": start_date,
        "end_date": end_date,
        "name": range_name,
    }
    return result
