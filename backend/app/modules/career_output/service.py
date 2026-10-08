"""Persistence orchestration for career-output records."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.core.time import utc_now
from app.modules.career_output.models import CareerOutput
from app.modules.career_output.schemas import CareerOutputCreate


def create_career_output(db: Session, payload: CareerOutputCreate) -> CareerOutput:
    item = CareerOutput(
        **payload.model_dump(exclude_none=True),
        logged_at=payload.logged_at or utc_now(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_career_output(db: Session) -> list[CareerOutput]:
    return list(db.scalars(select(CareerOutput).order_by(CareerOutput.logged_at)).all())


def delete_career_output(db: Session, output_id: int) -> None:
    item = db.get(CareerOutput, output_id)
    if item is None:
        raise NotFoundError("CAREER_OUTPUT_NOT_FOUND", {"output_id": output_id})
    db.delete(item)
    db.commit()
