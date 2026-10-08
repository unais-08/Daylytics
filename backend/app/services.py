from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import BusinessRuleError, ConflictError
from app.core.time import comparable_utc, utc_now
from app.models import Distraction, WorkSession


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
