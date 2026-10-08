"""Persistence orchestration for data export and deletion."""

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.exceptions import DangerousActionError
from app.models import CareerOutput, Distraction, SleepLog, WorkSession


def serialize_model(item) -> dict:
    return {
        column.name: (
            getattr(item, column.name).value
            if hasattr(getattr(item, column.name), "value")
            else getattr(item, column.name)
        )
        for column in item.__table__.columns
    }


def export_data(db: Session) -> dict[str, list[dict]]:
    return {
        "work_sessions": [
            serialize_model(x) for x in db.scalars(select(WorkSession)).all()
        ],
        "distractions": [
            serialize_model(x) for x in db.scalars(select(Distraction)).all()
        ],
        "sleep_logs": [serialize_model(x) for x in db.scalars(select(SleepLog)).all()],
        "career_outputs": [
            serialize_model(x) for x in db.scalars(select(CareerOutput)).all()
        ],
    }


def delete_data(db: Session, confirm: bool) -> None:
    if not confirm:
        raise DangerousActionError("CONFIRMATION_REQUIRED")
    for model in (WorkSession, Distraction, SleepLog, CareerOutput):
        db.execute(delete(model))
    db.commit()
