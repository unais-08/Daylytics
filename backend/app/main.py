from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.analytics import analyze
from app.config import get_settings
from app.database import get_db
from app.error_handlers import (
    app_error_handler,
    http_error_handler,
    integrity_error_handler,
    operational_error_handler,
    unhandled_error_handler,
    validation_error_handler,
)
from app.exceptions import (
    AppError,
    BusinessRuleError,
    ConflictError,
    DangerousActionError,
    InvalidParameterError,
    NotFoundError,
)
from app.logging_config import configure_logging
from app.middleware import RequestIDMiddleware
from app.models import (
    Activity,
    CareerOutput,
    Distraction,
    Prayer,
    PrayerLog,
    SleepLog,
    WorkSession,
)
from app.schemas import (
    CareerOutputCreate,
    DistractionCreate,
    DistractionResponse,
    PrayerUpdate,
    SessionCreate,
    SessionResponse,
    SleepCreate,
    StartDistraction,
    StartSession,
    StopSession,
    TodayResponse,
)
from app.services import (
    active_distraction,
    active_session,
    comparable_utc,
    duration_minutes,
    effective_deep_work,
    ensure_no_active,
    ensure_no_overlap,
    utc_now,
    validate_prayer_date,
    validate_time_window,
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


def local_date(value: datetime) -> date:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(ZoneInfo(get_settings().timezone)).date()


@app.get("/")
def root():
    return {"message": "Productivity API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


def _serialize_model(item):
    return {
        column.name: (
            getattr(item, column.name).value
            if hasattr(getattr(item, column.name), "value")
            else getattr(item, column.name)
        )
        for column in item.__table__.columns
    }


@app.get("/export")
def export_data(db: Session = Depends(get_db)):
    return {
        "work_sessions": [
            _serialize_model(x) for x in db.scalars(select(WorkSession)).all()
        ],
        "distractions": [
            _serialize_model(x) for x in db.scalars(select(Distraction)).all()
        ],
        "prayer_logs": [
            _serialize_model(x) for x in db.scalars(select(PrayerLog)).all()
        ],
        "sleep_logs": [_serialize_model(x) for x in db.scalars(select(SleepLog)).all()],
        "career_outputs": [
            _serialize_model(x) for x in db.scalars(select(CareerOutput)).all()
        ],
    }


@app.delete("/data", status_code=204)
def delete_data(confirm: bool = False, db: Session = Depends(get_db)):
    if not confirm:
        raise DangerousActionError("CONFIRMATION_REQUIRED")
    for model in (WorkSession, Distraction, PrayerLog, SleepLog, CareerOutput):
        db.execute(delete(model))
    db.commit()


@app.post("/sessions/start", response_model=SessionResponse, status_code=201)
def start_session(payload: StartSession, db: Session = Depends(get_db)):
    ensure_no_active(db, WorkSession, "work session")
    item = WorkSession(start_time=utc_now(), activity=payload.activity)
    db.add(item)
    db.commit()
    db.refresh(item)
    return session_response(item)


@app.post("/sessions/{session_id}/stop", response_model=SessionResponse)
def stop_session(session_id: int, payload: StopSession, db: Session = Depends(get_db)):
    item = db.get(WorkSession, session_id)
    if item is None:
        raise NotFoundError("SESSION_NOT_FOUND", {"session_id": session_id})
    if item.end_time is not None:
        raise ConflictError("SESSION_ALREADY_STOPPED", {"session_id": session_id})
    item.end_time = utc_now()
    item.focus_score = payload.focus_score
    item.deep_work = effective_deep_work(
        duration_minutes(item.start_time, item.end_time) or 0, payload.deep_work
    )
    db.commit()
    db.refresh(item)
    return session_response(item)


@app.post("/sessions", response_model=SessionResponse, status_code=201)
def create_session(payload: SessionCreate, db: Session = Depends(get_db)):
    minutes = duration_minutes(payload.start_time, payload.end_time) or 0
    item = WorkSession(
        activity=payload.activity,
        start_time=payload.start_time,
        end_time=payload.end_time,
        focus_score=payload.focus_score,
        deep_work=effective_deep_work(minutes, payload.deep_work),
    )
    validate_time_window(payload.start_time, payload.end_time, "session")
    ensure_no_overlap(db, WorkSession, payload.start_time, payload.end_time, "session")
    db.add(item)
    db.commit()
    db.refresh(item)
    return session_response(item)


@app.get("/sessions", response_model=list[SessionResponse])
def list_sessions(
    start_date: date | None = None,
    end_date: date | None = None,
    activity: Activity | None = None,
    db: Session = Depends(get_db),
):
    query = select(WorkSession).order_by(WorkSession.start_time)
    if start_date:
        query = query.where(
            WorkSession.start_time
            >= datetime.combine(start_date, datetime.min.time(), UTC)
        )
    if end_date:
        query = query.where(
            WorkSession.start_time
            < datetime.combine(end_date + timedelta(days=1), datetime.min.time(), UTC)
        )
    if activity:
        query = query.where(WorkSession.activity == activity)
    return [session_response(x) for x in db.scalars(query).all()]


@app.delete("/sessions/{session_id}", status_code=204)
def delete_session(session_id: int, db: Session = Depends(get_db)):
    item = db.get(WorkSession, session_id)
    if item is None:
        raise NotFoundError("SESSION_NOT_FOUND", {"session_id": session_id})
    db.delete(item)
    db.commit()


@app.post("/distractions/start", response_model=DistractionResponse, status_code=201)
def start_distraction(payload: StartDistraction, db: Session = Depends(get_db)):
    ensure_no_active(db, Distraction, "distraction")
    item = Distraction(start_time=utc_now(), category=payload.category)
    db.add(item)
    db.commit()
    db.refresh(item)
    return distraction_response(item)


@app.post("/distractions/{distraction_id}/stop", response_model=DistractionResponse)
def stop_distraction(distraction_id: int, db: Session = Depends(get_db)):
    item = db.get(Distraction, distraction_id)
    if item is None:
        raise NotFoundError("DISTRACTION_NOT_FOUND", {"distraction_id": distraction_id})
    if item.end_time is not None:
        raise ConflictError(
            "DISTRACTION_ALREADY_STOPPED", {"distraction_id": distraction_id}
        )
    item.end_time = utc_now()
    db.commit()
    db.refresh(item)
    return distraction_response(item)


@app.post("/distractions", response_model=DistractionResponse, status_code=201)
def create_distraction(payload: DistractionCreate, db: Session = Depends(get_db)):
    end = payload.end_time or utc_now()
    start = payload.start_time or end - timedelta(minutes=payload.minutes or 0)
    validate_time_window(start, end, "distraction")
    ensure_no_overlap(db, Distraction, start, end, "distraction")
    item = Distraction(category=payload.category, start_time=start, end_time=end)
    db.add(item)
    db.commit()
    db.refresh(item)
    return distraction_response(item)


@app.get("/distractions", response_model=list[DistractionResponse])
def list_distractions(db: Session = Depends(get_db)):
    return [
        distraction_response(x)
        for x in db.scalars(select(Distraction).order_by(Distraction.start_time)).all()
    ]


@app.delete("/distractions/{distraction_id}", status_code=204)
def delete_distraction(distraction_id: int, db: Session = Depends(get_db)):
    item = db.get(Distraction, distraction_id)
    if item is None:
        raise NotFoundError("DISTRACTION_NOT_FOUND", {"distraction_id": distraction_id})
    db.delete(item)
    db.commit()


@app.post("/sleep", status_code=201)
def create_sleep(payload: SleepCreate, db: Session = Depends(get_db)):
    minutes = (payload.wake_time - payload.sleep_start).total_seconds() / 60
    if minutes < 60 or minutes > 24 * 60:
        raise BusinessRuleError("SLEEP_DURATION_IMPLAUSIBLE")
    if comparable_utc(payload.wake_time) > utc_now() + timedelta(minutes=1):
        raise BusinessRuleError("FUTURE_TIME_NOT_ALLOWED")
    item = SleepLog(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, **payload.model_dump()}


@app.get("/sleep")
def list_sleep(db: Session = Depends(get_db)):
    return db.scalars(select(SleepLog).order_by(SleepLog.wake_time)).all()


@app.delete("/sleep/{sleep_id}", status_code=204)
def delete_sleep(sleep_id: int, db: Session = Depends(get_db)):
    item = db.get(SleepLog, sleep_id)
    if item is None:
        raise NotFoundError("SLEEP_LOG_NOT_FOUND", {"sleep_id": sleep_id})
    db.delete(item)
    db.commit()


@app.post("/career-output", status_code=201)
def create_career_output(payload: CareerOutputCreate, db: Session = Depends(get_db)):
    item = CareerOutput(
        **payload.model_dump(exclude_none=True),
        logged_at=payload.logged_at or utc_now(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/career-output")
def list_career_output(db: Session = Depends(get_db)):
    return db.scalars(select(CareerOutput).order_by(CareerOutput.logged_at)).all()


@app.delete("/career-output/{output_id}", status_code=204)
def delete_career_output(output_id: int, db: Session = Depends(get_db)):
    item = db.get(CareerOutput, output_id)
    if item is None:
        raise NotFoundError("CAREER_OUTPUT_NOT_FOUND", {"output_id": output_id})
    db.delete(item)
    db.commit()


@app.put("/prayers/{prayer_date}/{prayer}")
def update_prayer(
    prayer_date: date,
    prayer: Prayer,
    payload: PrayerUpdate,
    db: Session = Depends(get_db),
):
    validate_prayer_date(prayer_date)
    item = db.scalar(
        select(PrayerLog).where(
            PrayerLog.date == prayer_date,
            PrayerLog.prayer == prayer,
        )
    )
    if item is None:
        item = PrayerLog(date=prayer_date, prayer=prayer, status=payload.status)
        db.add(item)
    else:
        item.status = payload.status
    db.commit()
    db.refresh(item)
    return {"date": item.date, "prayer": item.prayer, "status": item.status}


@app.delete("/prayers/{prayer_date}/{prayer}", status_code=204)
def delete_prayer(prayer_date: date, prayer: Prayer, db: Session = Depends(get_db)):
    item = db.scalar(
        select(PrayerLog).where(
            PrayerLog.date == prayer_date,
            PrayerLog.prayer == prayer,
        )
    )
    if item is None:
        raise NotFoundError(
            "PRAYER_LOG_NOT_FOUND",
            {"date": prayer_date.isoformat(), "prayer": prayer.value},
        )
    db.delete(item)
    db.commit()


@app.get("/prayers")
def list_prayers(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
):
    query = select(PrayerLog).order_by(PrayerLog.date, PrayerLog.prayer)
    if start_date:
        query = query.where(PrayerLog.date >= start_date)
    if end_date:
        query = query.where(PrayerLog.date <= end_date)
    return db.scalars(query).all()


@app.get("/today", response_model=TodayResponse)
def today(db: Session = Depends(get_db)):
    today_date = datetime.now(ZoneInfo(get_settings().timezone)).date()
    sessions = db.scalars(select(WorkSession)).all()
    distractions = db.scalars(select(Distraction)).all()
    rows = db.scalars(select(PrayerLog).where(PrayerLog.date == today_date)).all()
    prayer_map = {row.prayer: row.status for row in rows}
    current_session = active_session(db)
    current_distraction = active_distraction(db)
    return TodayResponse(
        date=today_date,
        active_session=session_response(current_session) if current_session else None,
        active_distraction=distraction_response(current_distraction)
        if current_distraction
        else None,
        prayers={prayer: prayer_map.get(prayer) for prayer in Prayer},
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
