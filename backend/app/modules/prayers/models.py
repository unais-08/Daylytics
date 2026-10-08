"""SQLAlchemy models and enums owned by prayer tracking."""

from datetime import date
from enum import StrEnum

from sqlalchemy import Date, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Prayer(StrEnum):
    FAJR = "FAJR"
    DHUHR = "DHUHR"
    ASR = "ASR"
    MAGHRIB = "MAGHRIB"
    ISHA = "ISHA"


class PrayerStatus(StrEnum):
    COMPLETED = "completed"
    MISSED = "missed"


class PrayerLog(Base):
    __tablename__ = "prayer_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    prayer: Mapped[Prayer] = mapped_column(Enum(Prayer), nullable=False)
    status: Mapped[PrayerStatus] = mapped_column(Enum(PrayerStatus), nullable=False)
    __table_args__ = (UniqueConstraint("date", "prayer", name="uq_prayer_date_prayer"),)
