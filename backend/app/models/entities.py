from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Activity(StrEnum):
    DSA = "DSA"
    PROJECT = "PROJECT"
    JOB_APPLICATION = "JOB_APPLICATION"
    INTERVIEW_PREP = "INTERVIEW_PREP"
    LEARNING = "LEARNING"
    OTHER = "OTHER"


class DistractionCategory(StrEnum):
    YOUTUBE = "YOUTUBE"
    INSTAGRAM = "INSTAGRAM"
    GAMING = "GAMING"
    RANDOM_BROWSING = "RANDOM_BROWSING"
    PHONE = "PHONE"
    OTHER = "OTHER"


class Prayer(StrEnum):
    FAJR = "FAJR"
    DHUHR = "DHUHR"
    ASR = "ASR"
    MAGHRIB = "MAGHRIB"
    ISHA = "ISHA"


class PrayerStatus(StrEnum):
    COMPLETED = "completed"
    MISSED = "missed"


class CareerOutputType(StrEnum):
    DSA_PROBLEMS = "DSA_PROBLEMS"
    PROJECT_WORK = "PROJECT_WORK"
    APPLICATIONS = "APPLICATIONS"
    INTERVIEW = "INTERVIEW"
    MOCK_INTERVIEW = "MOCK_INTERVIEW"


class WorkSession(Base):
    __tablename__ = "work_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    activity: Mapped[Activity] = mapped_column(Enum(Activity), nullable=False)
    deep_work: Mapped[bool | None] = mapped_column(nullable=True)
    focus_score: Mapped[int | None] = mapped_column(Integer)
    __table_args__ = (
        CheckConstraint(
            "focus_score IS NULL OR focus_score BETWEEN 1 AND 5", name="ck_focus_score"
        ),
    )


class Distraction(Base):
    __tablename__ = "distractions"
    id: Mapped[int] = mapped_column(primary_key=True)
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    category: Mapped[DistractionCategory] = mapped_column(
        Enum(DistractionCategory), nullable=False
    )


class PrayerLog(Base):
    __tablename__ = "prayer_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    prayer: Mapped[Prayer] = mapped_column(Enum(Prayer), nullable=False)
    status: Mapped[PrayerStatus] = mapped_column(Enum(PrayerStatus), nullable=False)
    __table_args__ = (UniqueConstraint("date", "prayer", name="uq_prayer_date_prayer"),)


class SleepLog(Base):
    __tablename__ = "sleep_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    sleep_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    wake_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CareerOutput(Base):
    __tablename__ = "career_outputs"
    id: Mapped[int] = mapped_column(primary_key=True)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    type: Mapped[CareerOutputType] = mapped_column(
        Enum(CareerOutputType), nullable=False
    )
    count: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (CheckConstraint("count >= 1", name="ck_career_count"),)
