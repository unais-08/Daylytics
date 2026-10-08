"""HTTP routes for analytics requests."""

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.modules.analytics.service import analyze_request

router = APIRouter()


@router.get("/analytics/{kind}")
def analytics(
    kind: str,
    range: str = "30d",
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
):
    return analyze_request(db, kind, range, start_date, end_date)
