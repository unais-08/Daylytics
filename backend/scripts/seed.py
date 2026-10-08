from __future__ import annotations

import random
import sys
from datetime import UTC, datetime, time, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings
from app.core.database import Base, SessionLocal, engine
from app.models import (
    Activity,
    CareerOutput,
    CareerOutputType,
    Distraction,
    DistractionCategory,
    SleepLog,
    WorkSession,
)


def seed_database(days: int = 60, seed: int = 42) -> None:
    random.seed(seed)
    Base.metadata.create_all(bind=engine)
    settings = get_settings()
    today = datetime.now(UTC).date()
    with SessionLocal() as db:
        for model in (WorkSession, Distraction, SleepLog, CareerOutput):
            db.query(model).delete()
        for offset in range(days - 1, -1, -1):
            day = today - timedelta(days=offset)
            sessions = random.randint(1, 3)
            for index in range(sessions):
                start = datetime.combine(
                    day, time(hour=8 + index * 3, minute=15), tzinfo=UTC
                )
                minutes = random.randint(35, 110)
                db.add(
                    WorkSession(
                        start_time=start,
                        end_time=start + timedelta(minutes=minutes),
                        activity=random.choice(list(Activity)),
                        deep_work=minutes >= settings.deep_work_min_minutes,
                        focus_score=random.randint(2, 5),
                    )
                )
            leak_start = datetime.combine(day, time(13, 0), tzinfo=UTC)
            db.add(
                Distraction(
                    start_time=leak_start,
                    end_time=leak_start + timedelta(minutes=random.randint(5, 45)),
                    category=random.choice(list(DistractionCategory)),
                )
            )
            wake = datetime.combine(day, time(6, 30), tzinfo=UTC)
            db.add(
                SleepLog(
                    sleep_start=wake - timedelta(hours=random.randint(6, 9)),
                    wake_time=wake,
                )
            )
            db.add(
                CareerOutput(
                    logged_at=datetime.combine(day, time(18), tzinfo=UTC),
                    type=random.choice(list(CareerOutputType)),
                    count=random.randint(1, 3),
                )
            )
        db.commit()


if __name__ == "__main__":
    seed_database()
    print("Seeded 60 days of deterministic analytics data.")
