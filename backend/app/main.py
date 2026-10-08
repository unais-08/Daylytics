from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.analytics import analyze
from app.api.router import router as api_router
from app.core.config import get_settings
from app.core.database import get_db
from app.core.error_handlers import (
    app_error_handler,
    http_error_handler,
    integrity_error_handler,
    operational_error_handler,
    unhandled_error_handler,
    validation_error_handler,
)
from app.core.exceptions import (
    AppError,
    InvalidParameterError,
)
from app.core.logging import configure_logging
from app.core.middleware import RequestIDMiddleware
from app.core.time import duration_minutes
from app.models import (
    CareerOutput,
    Distraction,
    PrayerLog,
    SleepLog,
    WorkSession,
)
from app.schemas import (
    DistractionResponse,
    SessionResponse,
)

configure_logging()
app = FastAPI(title="Personal Analytics API", version="0.1.0")
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_exception_handler(Exception, unhandled_error_handler)
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(StarletteHTTPException, http_error_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(OperationalError, operational_error_handler)
app.include_router(api_router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
        description="Local-first personal analytics API.",
    )
    schema.setdefault("components", {}).setdefault("schemas", {})["ErrorResponse"] = {
        "title": "ErrorResponse",
        "type": "object",
        "required": ["error"],
        "properties": {
            "error": {
                "type": "object",
                "required": ["code", "message", "request_id"],
                "properties": {
                    "code": {"type": "string"},
                    "message": {"type": "string"},
                    "details": {"type": "object"},
                    "request_id": {"type": "string", "format": "uuid"},
                },
            }
        },
    }
    error_ref = {"$ref": "#/components/schemas/ErrorResponse"}
    for path in schema.get("paths", {}).values():
        for operation in path.values():
            if isinstance(operation, dict) and "responses" in operation:
                for status in ("400", "404", "409", "422", "500"):
                    operation["responses"].setdefault(
                        status,
                        {
                            "description": "Standard error response",
                            "content": {"application/json": {"schema": error_ref}},
                        },
                    )
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi


def session_response(item: WorkSession) -> SessionResponse:
    return SessionResponse.model_validate(item).model_copy(
        update={"duration_minutes": duration_minutes(item.start_time, item.end_time)}
    )


def distraction_response(item: Distraction) -> DistractionResponse:
    return DistractionResponse.model_validate(item).model_copy(
        update={"duration_minutes": duration_minutes(item.start_time, item.end_time)}
    )


def _analytics_frames(db: Session, start_date: date | None, end_date: date | None):
    settings = get_settings()
    zone = ZoneInfo(settings.timezone)
    session_rows = db.scalars(select(WorkSession)).all()
    distraction_rows = db.scalars(select(Distraction)).all()
    prayer_rows = db.scalars(select(PrayerLog)).all()
    sleep_rows = db.scalars(select(SleepLog)).all()
    career_rows = db.scalars(select(CareerOutput)).all()

    def local_dt(value: datetime) -> datetime:
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(zone)

    def in_range(day: date) -> bool:
        return (start_date is None or day >= start_date) and (
            end_date is None or day <= end_date
        )

    sessions = []
    for item in session_rows:
        local = local_dt(item.start_time)
        if in_range(local.date()) and item.end_time is not None:
            sessions.append(
                {
                    "local_date": local.date(),
                    "weekday": local.weekday(),
                    "hour": local.hour,
                    "minutes": duration_minutes(item.start_time, item.end_time) or 0,
                    "deep_work": bool(item.deep_work),
                    "focus": item.focus_score,
                }
            )
    distractions = []
    for item in distraction_rows:
        local = local_dt(item.start_time)
        if in_range(local.date()) and item.end_time is not None:
            distractions.append(
                {
                    "local_date": local.date(),
                    "weekday": local.weekday(),
                    "minutes": duration_minutes(item.start_time, item.end_time) or 0,
                    "category": item.category.value,
                }
            )
    prayers = [
        {
            "local_date": item.date,
            "weekday": item.date.weekday(),
            "prayer": item.prayer.value,
            "status": item.status.value,
        }
        for item in prayer_rows
        if in_range(item.date)
    ]
    sleep = []
    for item in sleep_rows:
        wake = local_dt(item.wake_time)
        if in_range(wake.date()):
            sleep.append(
                {
                    "local_date": wake.date(),
                    "next_day": wake.date() + timedelta(days=1),
                    "sleep_minutes": duration_minutes(item.sleep_start, item.wake_time)
                    or 0,
                }
            )
    career = []
    for item in career_rows:
        local = local_dt(item.logged_at)
        if in_range(local.date()):
            career.append(
                {
                    "local_date": local.date(),
                    "count": item.count,
                    "type": item.type.value,
                }
            )

    def frame(rows, columns):
        return pd.DataFrame(rows, columns=columns)

    return (
        frame(
            sessions, ["local_date", "weekday", "hour", "minutes", "deep_work", "focus"]
        ),
        frame(distractions, ["local_date", "weekday", "minutes", "category"]),
        frame(prayers, ["local_date", "weekday", "prayer", "status"]),
        frame(sleep, ["local_date", "next_day", "sleep_minutes"]),
        frame(career, ["local_date", "count", "type"]),
    )


@app.get("/analytics/{kind}")
def analytics(
    kind: str,
    range: str = "30d",
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
):
    today_date = datetime.now(ZoneInfo(get_settings().timezone)).date()
    if range in {"today", "7d", "30d"}:
        days = {"today": 0, "7d": 6, "30d": 29}[range]
        start_date = today_date - timedelta(days=days)
        end_date = today_date
    elif range != "custom":
        raise InvalidParameterError(
            "INVALID_FILTER",
            details={"allowed_ranges": ["today", "7d", "30d", "custom"]},
        )
    if range == "custom" and (start_date is None or end_date is None):
        raise InvalidParameterError(
            "INVALID_DATE_RANGE",
            "Custom analytics ranges require both start_date and end_date.",
        )
    if start_date and end_date and end_date < start_date:
        raise InvalidParameterError("INVALID_DATE_RANGE")
    if start_date and end_date and (end_date - start_date).days > 366:
        raise InvalidParameterError("RANGE_TOO_LARGE")
    allowed = {
        "time-leaks",
        "deep-work",
        "best-worst-days",
        "focus-by-time",
        "prayers",
        "career-output",
        "weekday-weekend",
        "sleep-focus",
        "trends",
        "overview",
    }
    if kind not in allowed:
        raise InvalidParameterError(
            "INVALID_ANALYSIS_NAME",
            details={"allowed_names": sorted(allowed)},
        )
    frames = _analytics_frames(db, start_date, end_date)
    result = analyze(kind, *frames)
    result["range"] = {"start_date": start_date, "end_date": end_date, "name": range}
    return result
