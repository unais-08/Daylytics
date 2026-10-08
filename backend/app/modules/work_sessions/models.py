"""SQLAlchemy models and enums owned by work sessions."""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import CheckConstraint, DateTime, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Activity(StrEnum):
    DSA = "DSA"
    PROJECT = "PROJECT"
    JOB_APPLICATION = "JOB_APPLICATION"
    INTERVIEW_PREP = "INTERVIEW_PREP"
    LEARNING = "LEARNING"
    OTHER = "OTHER"


class WorkSession(Base):
    __tablename__ = "work_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    activity: Mapped[Activity] = mapped_column(Enum(Activity), nullable=False)
    deep_work: Mapped[bool | None] = mapped_column(nullable=True)
    focus_score: Mapped[int | None] = mapped_column(Integer)
    __table_args__ = (
        CheckConstraint(
            "focus_score IS NULL OR focus_score BETWEEN 1 AND 5",
            name="ck_focus_score",
        ),
    )
