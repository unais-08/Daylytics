"""Database reads for distractions."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.distractions.models import Distraction


def get_distraction(db: Session, distraction_id: int) -> Distraction | None:
    return db.get(Distraction, distraction_id)


def get_active_distraction(db: Session) -> Distraction | None:
    return db.scalar(select(Distraction).where(Distraction.end_time.is_(None)))


def list_distractions(db: Session) -> list[Distraction]:
    return list(db.scalars(select(Distraction).order_by(Distraction.start_time)).all())
