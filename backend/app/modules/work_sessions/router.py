"""HTTP routes for work sessions."""

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.modules.work_sessions import service
from app.modules.work_sessions.models import Activity
from app.modules.work_sessions.schemas import (
    SessionCreate,
    SessionResponse,
    StartSession,
    StopSession,
)

router = APIRouter()


@router.post("/sessions/start", response_model=SessionResponse, status_code=201)
def start_session(payload: StartSession, db: Session = Depends(get_db)):
    return service.start_session(db, payload)


@router.post("/sessions/{session_id}/stop", response_model=SessionResponse)
def stop_session(session_id: int, payload: StopSession, db: Session = Depends(get_db)):
    return service.stop_session(db, session_id, payload)


@router.post("/sessions", response_model=SessionResponse, status_code=201)
def create_session(payload: SessionCreate, db: Session = Depends(get_db)):
    return service.create_session(db, payload)


@router.get("/sessions", response_model=list[SessionResponse])
def list_sessions(
    start_date: date | None = None,
    end_date: date | None = None,
    activity: Activity | None = None,
    db: Session = Depends(get_db),
):
    return service.list_session_responses(db, start_date, end_date, activity)


@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(session_id: int, db: Session = Depends(get_db)):
    service.delete_session(db, session_id)
