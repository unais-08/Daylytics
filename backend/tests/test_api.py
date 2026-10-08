from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.core.database import Base, engine
from app.main import app


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_health_and_session_lifecycle():
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}
        started = client.post("/sessions/start", json={"activity": "DSA"})
        assert started.status_code == 201
        session_id = started.json()["id"]
        assert (
            client.post("/sessions/start", json={"activity": "PROJECT"}).status_code
            == 409
        )
        stopped = client.post(f"/sessions/{session_id}/stop", json={"focus_score": 4})
        assert stopped.status_code == 200
        assert stopped.json()["focus_score"] == 4
        assert stopped.json()["duration_minutes"] is not None


def test_manual_entries_and_validation():
    start = datetime.now(UTC) - timedelta(minutes=30)
    end = datetime.now(UTC)
    with TestClient(app) as client:
        response = client.post(
            "/sessions",
            json={
                "activity": "PROJECT",
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
                "focus_score": 5,
            },
        )
        assert response.status_code == 201
        assert response.json()["deep_work"] is True
        assert (
            client.post(
                "/sessions",
                json={
                    "activity": "PROJECT",
                    "start_time": end.isoformat(),
                    "end_time": start.isoformat(),
                },
            ).status_code
            == 422
        )
        assert (
            client.post(
                "/distractions",
                json={"category": "YOUTUBE", "minutes": 10},
            ).status_code
            == 201
        )
        assert (
            client.post(
                "/distractions/start",
                json={"category": "PHONE"},
            ).status_code
            == 201
        )
        assert (
            client.post(
                "/distractions/start",
                json={"category": "GAMING"},
            ).status_code
            == 409
        )

