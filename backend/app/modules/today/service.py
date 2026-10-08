"""Read-only orchestration for today's dashboard."""

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.time import duration_minutes, local_date
from app.models import Distraction, WorkSession
from app.modules.distractions.service import to_response as distraction_response
from app.modules.today.schemas import TodayResponse
from app.modules.work_sessions.service import to_response as session_response
from app.services import active_distraction, active_session


def get_today(db: Session) -> TodayResponse:
    today_date = datetime.now(ZoneInfo(get_settings().timezone)).date()
    sessions = db.scalars(select(WorkSession)).all()
    distractions = db.scalars(select(Distraction)).all()
    current_session = active_session(db)
    current_distraction = active_distraction(db)
    return TodayResponse(
        date=today_date,
        active_session=session_response(current_session) if current_session else None,
        active_distraction=distraction_response(current_distraction)
        if current_distraction
        else None,
        totals={
            "work_minutes": round(
                sum(
                    duration_minutes(x.start_time, x.end_time) or 0
                    for x in sessions
                    if local_date(x.start_time) == today_date
                ),
                2,
            ),
            "distraction_minutes": round(
                sum(
                    duration_minutes(x.start_time, x.end_time) or 0
                    for x in distractions
                    if local_date(x.start_time) == today_date
                ),
                2,
            ),
        },
    )
