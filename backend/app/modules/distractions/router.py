"""HTTP routes for distractions."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.modules.distractions import service
from app.modules.distractions.schemas import (
    DistractionCreate,
    DistractionResponse,
    StartDistraction,
)

router = APIRouter()


@router.post("/distractions/start", response_model=DistractionResponse, status_code=201)
def start_distraction(payload: StartDistraction, db: Session = Depends(get_db)):
    return service.start_distraction(db, payload)


@router.post("/distractions/{distraction_id}/stop", response_model=DistractionResponse)
def stop_distraction(distraction_id: int, db: Session = Depends(get_db)):
    return service.stop_distraction(db, distraction_id)


@router.post("/distractions", response_model=DistractionResponse, status_code=201)
def create_distraction(payload: DistractionCreate, db: Session = Depends(get_db)):
    return service.create_distraction(db, payload)


@router.get("/distractions", response_model=list[DistractionResponse])
def list_distractions(db: Session = Depends(get_db)):
    return service.list_distraction_responses(db)


@router.delete("/distractions/{distraction_id}", status_code=204)
def delete_distraction(distraction_id: int, db: Session = Depends(get_db)):
    service.delete_distraction(db, distraction_id)
