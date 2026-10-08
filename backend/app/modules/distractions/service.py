"""Business rules and persistence orchestration for distractions."""

from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.core.time import duration_minutes, utc_now
from app.modules.distractions import queries
from app.modules.distractions.models import Distraction
from app.modules.distractions.schemas import (
    DistractionCreate,
    DistractionResponse,
    StartDistraction,
)
from app.services import ensure_no_active, ensure_no_overlap, validate_time_window


def to_response(item: Distraction) -> DistractionResponse:
    return DistractionResponse.model_validate(item).model_copy(
        update={"duration_minutes": duration_minutes(item.start_time, item.end_time)}
    )


def start_distraction(db: Session, payload: StartDistraction) -> DistractionResponse:
    ensure_no_active(db, Distraction, "distraction")
    item = Distraction(start_time=utc_now(), category=payload.category)
    db.add(item)
    db.commit()
    db.refresh(item)
    return to_response(item)


def stop_distraction(db: Session, distraction_id: int) -> DistractionResponse:
    item = queries.get_distraction(db, distraction_id)
    if item is None:
        raise NotFoundError("DISTRACTION_NOT_FOUND", {"distraction_id": distraction_id})
    if item.end_time is not None:
        raise ConflictError(
            "DISTRACTION_ALREADY_STOPPED", {"distraction_id": distraction_id}
        )
    item.end_time = utc_now()
    db.commit()
    db.refresh(item)
    return to_response(item)


def create_distraction(db: Session, payload: DistractionCreate) -> DistractionResponse:
    end = payload.end_time or utc_now()
    start = payload.start_time or end - timedelta(minutes=payload.minutes or 0)
    validate_time_window(start, end, "distraction")
    ensure_no_overlap(db, Distraction, start, end, "distraction")
    item = Distraction(category=payload.category, start_time=start, end_time=end)
    db.add(item)
    db.commit()
    db.refresh(item)
    return to_response(item)


def list_distraction_responses(db: Session) -> list[DistractionResponse]:
    return [to_response(item) for item in queries.list_distractions(db)]


def delete_distraction(db: Session, distraction_id: int) -> None:
    item = queries.get_distraction(db, distraction_id)
    if item is None:
        raise NotFoundError("DISTRACTION_NOT_FOUND", {"distraction_id": distraction_id})
    db.delete(item)
    db.commit()
