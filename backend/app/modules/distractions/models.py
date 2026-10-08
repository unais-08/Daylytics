"""SQLAlchemy models and enums owned by distractions."""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DistractionCategory(StrEnum):
    YOUTUBE = "YOUTUBE"
    INSTAGRAM = "INSTAGRAM"
    GAMING = "GAMING"
    RANDOM_BROWSING = "RANDOM_BROWSING"
    PHONE = "PHONE"
    OTHER = "OTHER"


class Distraction(Base):
    __tablename__ = "distractions"
    id: Mapped[int] = mapped_column(primary_key=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    category: Mapped[DistractionCategory] = mapped_column(
        Enum(DistractionCategory), nullable=False
    )
