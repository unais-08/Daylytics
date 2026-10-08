"""Top-level HTTP router for cross-feature and feature endpoints."""

from fastapi import APIRouter

from app.modules.analytics.router import router as analytics_router
from app.modules.career_output.router import router as career_output_router
from app.modules.data_admin.router import router as data_admin_router
from app.modules.distractions.router import router as distractions_router
from app.modules.prayers.router import router as prayers_router
from app.modules.sleep.router import router as sleep_router
from app.modules.today.router import router as today_router
from app.modules.work_sessions.router import router as work_sessions_router

router = APIRouter()


@router.get("/")
def root():
    return {"message": "Productivity API is running"}


@router.get("/health")
def health():
    return {"status": "ok"}


router.include_router(work_sessions_router)
router.include_router(distractions_router)
router.include_router(sleep_router)
router.include_router(career_output_router)
router.include_router(analytics_router)
router.include_router(prayers_router)
router.include_router(today_router)
router.include_router(data_admin_router)
