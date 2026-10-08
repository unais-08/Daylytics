from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.exceptions import BusinessRuleError, ConflictError
from app.models import Distraction, WorkSession


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


def active_session(db: Session) -> WorkSession | None:
    return db.scalar(select(WorkSession).where(WorkSession.end_time.is_(None)))


def active_distraction(db: Session) -> Distraction | None:
    return db.scalar(select(Distraction).where(Distraction.end_time.is_(None)))


def ensure_no_active(db: Session, model, label: str) -> None:
    item = db.scalar(select(model).where(model.end_time.is_(None)))
    if item is not None:
        code = (
            "SESSION_ALREADY_ACTIVE"
            if model is WorkSession
            else "DISTRACTION_ALREADY_ACTIVE"
        )
        raise ConflictError(code, {"conflicting_id": item.id})


def effective_deep_work(minutes: float, explicit: bool | None) -> bool:
    return (
        explicit
        if explicit is not None
        else minutes >= get_settings().deep_work_min_minutes
    )


def validate_time_window(start: datetime, end: datetime, kind: str) -> None:
    start = comparable_utc(start)
    end = comparable_utc(end)
    if end <= start:
        raise BusinessRuleError("INVALID_TIME_RANGE")
    if start > utc_now() + timedelta(minutes=1) or end > utc_now() + timedelta(
        minutes=1
    ):
        raise BusinessRuleError("FUTURE_TIME_NOT_ALLOWED")
    maximum = 16 * 60 if kind == "session" else 24 * 60
    if (end - start).total_seconds() / 60 > maximum:
        code = "SESSION_TOO_LONG" if kind == "session" else "DISTRACTION_TOO_LONG"
        raise BusinessRuleError(code)


def ensure_no_overlap(
    db: Session, model, start: datetime, end: datetime, kind: str
) -> None:
    item = db.scalar(
        select(model).where(model.start_time < end, model.end_time > start).limit(1)
    )
    if item is not None:
        code = "OVERLAPPING_SESSION" if kind == "session" else "OVERLAPPING_DISTRACTION"
        raise BusinessRuleError(code, details={"conflicting_id": item.id})


def validate_prayer_date(value: date) -> None:
    if value > datetime.now(UTC).date():
        raise BusinessRuleError("PRAYER_DATE_IN_FUTURE")
