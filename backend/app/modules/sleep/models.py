"""SQLAlchemy model owned by sleep tracking."""

from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SleepLog(Base):
    __tablename__ = "sleep_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    sleep_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    wake_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
