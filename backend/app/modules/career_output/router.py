"""HTTP routes for career-output records."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.modules.career_output import service
from app.modules.career_output.schemas import CareerOutputCreate

router = APIRouter()


@router.post("/career-output", status_code=201)
def create_career_output(payload: CareerOutputCreate, db: Session = Depends(get_db)):
    return service.create_career_output(db, payload)


@router.get("/career-output")
def list_career_output(db: Session = Depends(get_db)):
    return service.list_career_output(db)


@router.delete("/career-output/{output_id}", status_code=204)
def delete_career_output(output_id: int, db: Session = Depends(get_db)):
    service.delete_career_output(db, output_id)
