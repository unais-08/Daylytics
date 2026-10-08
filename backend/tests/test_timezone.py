from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.core.database import Base, engine
from app.main import app


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_today_uses_configured_local_date_for_utc_evening_session():
    start = datetime(2026, 10, 7, 19, 0, tzinfo=UTC)
    end = start + timedelta(minutes=30)
    with TestClient(app) as client:
        response = client.post(
            "/sessions",
            json={
                "activity": "DSA",
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
                "focus_score": 4,
            },
        )
        assert response.status_code == 201
        today = client.get("/today")
        assert today.status_code == 200
        assert today.json()["date"] == "2026-10-08"
        assert today.json()["totals"]["work_minutes"] == 30


def test_analytics_today_uses_configured_local_date():
    start = datetime(2026, 10, 7, 19, 0, tzinfo=UTC)
    end = start + timedelta(minutes=30)
    with TestClient(app) as client:
        client.post(
            "/sessions",
            json={
                "activity": "DSA",
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
                "focus_score": 4,
            },
        )
        response = client.get("/analytics/deep-work?range=today")
        assert response.status_code == 200
        assert response.json()["range"]["start_date"] == "2026-10-08"
        assert response.json()["result"]["total_minutes"] == 30
