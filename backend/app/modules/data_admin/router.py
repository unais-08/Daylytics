"""HTTP routes for data portability and reset."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.modules.data_admin.service import (
    delete_data as delete_data_service,
)
from app.modules.data_admin.service import (
    export_data as export_data_service,
)

router = APIRouter()


@router.get("/export")
def export_data(db: Session = Depends(get_db)):
    return export_data_service(db)


@router.delete("/data", status_code=204)
def delete_data(confirm: bool = False, db: Session = Depends(get_db)):
    delete_data_service(db, confirm)
