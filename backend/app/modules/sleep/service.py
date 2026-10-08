"""Business rules and persistence orchestration for sleep logs."""

from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError
from app.core.time import comparable_utc, utc_now
from app.modules.sleep.models import SleepLog
from app.modules.sleep.schemas import SleepCreate


def create_sleep(db: Session, payload: SleepCreate) -> dict:
    minutes = (payload.wake_time - payload.sleep_start).total_seconds() / 60
    if minutes < 60 or minutes > 24 * 60:
        raise BusinessRuleError("SLEEP_DURATION_IMPLAUSIBLE")
    if comparable_utc(payload.wake_time) > utc_now() + timedelta(minutes=1):
        raise BusinessRuleError("FUTURE_TIME_NOT_ALLOWED")
    item = SleepLog(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, **payload.model_dump()}


def list_sleep(db: Session) -> list[SleepLog]:
    return list(db.scalars(select(SleepLog).order_by(SleepLog.wake_time)).all())


def delete_sleep(db: Session, sleep_id: int) -> None:
    item = db.get(SleepLog, sleep_id)
    if item is None:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("SLEEP_LOG_NOT_FOUND", {"sleep_id": sleep_id})
    db.delete(item)
    db.commit()
