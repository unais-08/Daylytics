"""Business rules and persistence orchestration for work sessions."""

from datetime import date

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.core.time import duration_minutes, utc_now
from app.modules.work_sessions import queries
from app.modules.work_sessions.models import Activity, WorkSession
from app.modules.work_sessions.schemas import (
    SessionCreate,
    SessionResponse,
    StartSession,
    StopSession,
)
from app.services import (
    effective_deep_work,
    ensure_no_active,
    ensure_no_overlap,
    validate_time_window,
)


def to_response(item: WorkSession) -> SessionResponse:
    return SessionResponse.model_validate(item).model_copy(
        update={"duration_minutes": duration_minutes(item.start_time, item.end_time)}
    )


def start_session(db: Session, payload: StartSession) -> SessionResponse:
    ensure_no_active(db, WorkSession, "work session")
    item = WorkSession(start_time=utc_now(), activity=payload.activity)
    db.add(item)
    db.commit()
    db.refresh(item)
    return to_response(item)


def stop_session(db: Session, session_id: int, payload: StopSession) -> SessionResponse:
    item = queries.get_session(db, session_id)
    if item is None:
        raise NotFoundError("SESSION_NOT_FOUND", {"session_id": session_id})
    if item.end_time is not None:
        raise ConflictError("SESSION_ALREADY_STOPPED", {"session_id": session_id})
    item.end_time = utc_now()
    item.focus_score = payload.focus_score
    item.deep_work = effective_deep_work(
        duration_minutes(item.start_time, item.end_time) or 0, payload.deep_work
    )
    db.commit()
    db.refresh(item)
    return to_response(item)


def create_session(db: Session, payload: SessionCreate) -> SessionResponse:
    minutes = duration_minutes(payload.start_time, payload.end_time) or 0
    validate_time_window(payload.start_time, payload.end_time, "session")
    ensure_no_overlap(db, WorkSession, payload.start_time, payload.end_time, "session")
    item = WorkSession(
        activity=payload.activity,
        start_time=payload.start_time,
        end_time=payload.end_time,
        focus_score=payload.focus_score,
        deep_work=effective_deep_work(minutes, payload.deep_work),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return to_response(item)


def list_session_responses(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None,
    activity: Activity | None = None,
) -> list[SessionResponse]:
    return [to_response(item) for item in queries.list_sessions(db, start_date, end_date, activity)]


def delete_session(db: Session, session_id: int) -> None:
    item = queries.get_session(db, session_id)
    if item is None:
        raise NotFoundError("SESSION_NOT_FOUND", {"session_id": session_id})
    db.delete(item)
    db.commit()
