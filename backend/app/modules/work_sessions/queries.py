"""Database reads for work sessions."""

from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.work_sessions.models import Activity, WorkSession


def get_session(db: Session, session_id: int) -> WorkSession | None:
    return db.get(WorkSession, session_id)


def get_active_session(db: Session) -> WorkSession | None:
    return db.scalar(select(WorkSession).where(WorkSession.end_time.is_(None)))


def list_sessions(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None,
    activity: Activity | None = None,
) -> list[WorkSession]:
    query = select(WorkSession).order_by(WorkSession.start_time)
    if start_date:
        query = query.where(
            WorkSession.start_time >= datetime.combine(start_date, datetime.min.time(), UTC)
        )
    if end_date:
        query = query.where(
            WorkSession.start_time
            < datetime.combine(end_date + timedelta(days=1), datetime.min.time(), UTC)
        )
    if activity:
        query = query.where(WorkSession.activity == activity)
    return list(db.scalars(query).all())
