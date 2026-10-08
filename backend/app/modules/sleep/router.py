"""HTTP routes for sleep logs."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.modules.sleep import service
from app.modules.sleep.schemas import SleepCreate

router = APIRouter()


@router.post("/sleep", status_code=201)
def create_sleep(payload: SleepCreate, db: Session = Depends(get_db)):
    return service.create_sleep(db, payload)


@router.get("/sleep")
def list_sleep(db: Session = Depends(get_db)):
    return service.list_sleep(db)


@router.delete("/sleep/{sleep_id}", status_code=204)
def delete_sleep(sleep_id: int, db: Session = Depends(get_db)):
    service.delete_sleep(db, sleep_id)
