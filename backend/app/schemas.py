from datetime import UTC, date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models import (
    Activity,
    CareerOutputType,
    DistractionCategory,
    Prayer,
    PrayerStatus,
)


def _utc(value: datetime) -> datetime:
    return (value if value.tzinfo else value.replace(tzinfo=UTC)).astimezone(UTC)


class StartSession(BaseModel):
    activity: Activity


class StopSession(BaseModel):
    focus_score: int = Field(ge=1, le=5)
    deep_work: bool | None = None


class SessionCreate(BaseModel):
    activity: Activity
    start_time: datetime
    end_time: datetime
    focus_score: int | None = Field(default=None, ge=1, le=5)
    deep_work: bool | None = None

    @model_validator(mode="after")
    def validate_times(self):
        if _utc(self.end_time) <= _utc(self.start_time):
            raise ValueError("end_time must be after start_time")
        return self


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    activity: Activity
    start_time: datetime
    end_time: datetime | None
    deep_work: bool | None
    focus_score: int | None
    duration_minutes: float | None = None


class StartDistraction(BaseModel):
    category: DistractionCategory


class DistractionCreate(BaseModel):
    category: DistractionCategory
    minutes: int | None = Field(default=None, ge=1, le=1440)
    start_time: datetime | None = None
    end_time: datetime | None = None

    @model_validator(mode="after")
    def validate_input(self):
        if self.minutes is None and (self.start_time is None or self.end_time is None):
            raise ValueError("provide minutes or both start_time and end_time")
        if self.minutes is not None and (
            self.start_time is not None or self.end_time is not None
        ):
            raise ValueError("provide either minutes or explicit times, not both")
        if (
            self.start_time
            and self.end_time
            and _utc(self.end_time) <= _utc(self.start_time)
        ):
            raise ValueError("end_time must be after start_time")
        return self


class DistractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category: DistractionCategory
    start_time: datetime
    end_time: datetime | None
    duration_minutes: float | None = None


class SleepCreate(BaseModel):
    sleep_start: datetime
    wake_time: datetime

    @model_validator(mode="after")
    def validate_times(self):
        if _utc(self.wake_time) <= _utc(self.sleep_start):
            raise ValueError("wake_time must be after sleep_start")
        return self


class CareerOutputCreate(BaseModel):
    logged_at: datetime | None = None
    type: CareerOutputType
    count: int = Field(ge=1)
    note: str | None = None


class PrayerUpdate(BaseModel):
    status: PrayerStatus


class TodayResponse(BaseModel):
    date: date
    active_session: SessionResponse | None
    active_distraction: DistractionResponse | None
    prayers: dict[Prayer, PrayerStatus | None]
    totals: dict[str, float]


class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict | None = None
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorBody
