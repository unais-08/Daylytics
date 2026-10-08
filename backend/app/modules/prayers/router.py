"""HTTP routes for prayer logs."""

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.modules.prayers import service
from app.modules.prayers.models import Prayer
from app.modules.prayers.schemas import PrayerUpdate

router = APIRouter()


@router.put("/prayers/{prayer_date}/{prayer}")
def update_prayer(
    prayer_date: date,
    prayer: Prayer,
    payload: PrayerUpdate,
    db: Session = Depends(get_db),
):
    return service.update_prayer(db, prayer_date, prayer, payload)


@router.delete("/prayers/{prayer_date}/{prayer}", status_code=204)
def delete_prayer(prayer_date: date, prayer: Prayer, db: Session = Depends(get_db)):
    service.delete_prayer(db, prayer_date, prayer)


@router.get("/prayers")
def list_prayers(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
):
    return service.list_prayers(db, start_date, end_date)
