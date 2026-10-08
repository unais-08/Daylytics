"""SQLAlchemy models and enums owned by career output."""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CareerOutputType(StrEnum):
    DSA_PROBLEMS = "DSA_PROBLEMS"
    PROJECT_WORK = "PROJECT_WORK"
    APPLICATIONS = "APPLICATIONS"
    INTERVIEW = "INTERVIEW"
    MOCK_INTERVIEW = "MOCK_INTERVIEW"


class CareerOutput(Base):
    __tablename__ = "career_outputs"
    id: Mapped[int] = mapped_column(primary_key=True)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    type: Mapped[CareerOutputType] = mapped_column(Enum(CareerOutputType), nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[str | None] = mapped_column(Text)
