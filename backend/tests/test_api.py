from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.database import Base, engine
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


def test_today_contains_all_prayer_slots():
    with TestClient(app) as client:
        response = client.get("/today")
        assert response.status_code == 200
        assert set(response.json()["prayers"]) == {
            "FAJR",
            "DHUHR",
            "ASR",
            "MAGHRIB",
            "ISHA",
        }


def test_prayer_update_is_idempotent_and_delete_unlogs():
    prayer_date = "2026-10-08"
    with TestClient(app) as client:
        first = client.put(
            f"/prayers/{prayer_date}/FAJR",
            json={"status": "completed"},
        )
        second = client.put(
            f"/prayers/{prayer_date}/FAJR",
            json={"status": "missed"},
        )
        assert first.status_code == 200
        assert second.status_code == 200
        assert second.json()["status"] == "missed"
        assert len(client.get("/prayers").json()) == 1
        assert client.delete(f"/prayers/{prayer_date}/FAJR").status_code == 204
        assert client.get("/prayers").json() == []


def test_prayer_validation_and_missing_delete():
    with TestClient(app) as client:
        assert (
            client.put(
                "/prayers/2026-10-08/FAJR",
                json={"status": "unknown"},
            ).status_code
            == 422
        )
        assert client.delete("/prayers/2026-10-08/FAJR").status_code == 404
