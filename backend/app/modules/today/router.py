"""HTTP route for today's dashboard."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.modules.today.schemas import TodayResponse
from app.modules.today.service import get_today

router = APIRouter()


@router.get("/today", response_model=TodayResponse)
def today(db: Session = Depends(get_db)):
    return get_today(db)
