"""Business rules and persistence orchestration for prayer logs."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.modules.prayers.models import Prayer, PrayerLog
from app.modules.prayers.schemas import PrayerUpdate
from app.services import validate_prayer_date


def update_prayer(
    db: Session, prayer_date: date, prayer: Prayer, payload: PrayerUpdate
) -> dict:
    validate_prayer_date(prayer_date)
    item = db.scalar(
        select(PrayerLog).where(
            PrayerLog.date == prayer_date,
            PrayerLog.prayer == prayer,
        )
    )
    if item is None:
        item = PrayerLog(date=prayer_date, prayer=prayer, status=payload.status)
        db.add(item)
    else:
        item.status = payload.status
    db.commit()
    db.refresh(item)
    return {"date": item.date, "prayer": item.prayer, "status": item.status}


def delete_prayer(db: Session, prayer_date: date, prayer: Prayer) -> None:
    item = db.scalar(
        select(PrayerLog).where(
            PrayerLog.date == prayer_date,
            PrayerLog.prayer == prayer,
        )
    )
    if item is None:
        raise NotFoundError(
            "PRAYER_LOG_NOT_FOUND",
            {"date": prayer_date.isoformat(), "prayer": prayer.value},
        )
    db.delete(item)
    db.commit()


def list_prayers(
    db: Session, start_date: date | None = None, end_date: date | None = None
) -> list[PrayerLog]:
    query = select(PrayerLog).order_by(PrayerLog.date, PrayerLog.prayer)
    if start_date:
        query = query.where(PrayerLog.date >= start_date)
    if end_date:
        query = query.where(PrayerLog.date <= end_date)
    return list(db.scalars(query).all())
