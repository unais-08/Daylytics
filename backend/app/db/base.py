"""Import every model so Alembic sees the complete application metadata."""

from app.core.database import Base
from app.modules.career_output.models import CareerOutput
from app.modules.distractions.models import Distraction
from app.modules.prayers.models import PrayerLog
from app.modules.sleep.models import SleepLog
from app.modules.work_sessions.models import WorkSession

__all__ = [
    "Base",
    "CareerOutput",
    "Distraction",
    "PrayerLog",
    "SleepLog",
    "WorkSession",
]
