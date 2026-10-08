from fastapi.testclient import TestClient

from app.core.database import Base, engine
from app.main import app


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_request_id_and_validation_error_shape():
    with TestClient(app) as client:
        response = client.post("/sessions", json={"activity": "DSA"})
        assert response.status_code == 422
        payload = response.json()["error"]
        assert payload["code"] == "VALIDATION_ERROR"
        assert payload["request_id"] == response.headers["X-Request-ID"]
        assert payload["details"]["fields"][0]["field"] == "start_time"


def test_unknown_route_and_method_error_shape():
    with TestClient(app) as client:
        missing = client.get("/not-a-real-route")
        assert missing.status_code == 404
        assert missing.json()["error"]["code"] == "ROUTE_NOT_FOUND"
        assert missing.json()["error"]["request_id"] == missing.headers["X-Request-ID"]
        wrong_method = client.patch("/health")
        assert wrong_method.status_code == 405
        assert wrong_method.json()["error"]["code"] == "METHOD_NOT_ALLOWED"


def test_incoming_request_id_is_preserved():
    request_id = "12345678-1234-4234-8234-123456789012"
    with TestClient(app) as client:
        response = client.get("/health", headers={"X-Request-ID": request_id})
        assert response.headers["X-Request-ID"] == request_id


def test_domain_errors_use_stable_codes():
    with TestClient(app) as client:
        assert client.delete("/data").json()["error"]["code"] == "CONFIRMATION_REQUIRED"
        assert (
            client.delete("/sessions/999").json()["error"]["code"]
            == "SESSION_NOT_FOUND"
        )
        assert (
            client.delete("/distractions/999").json()["error"]["code"]
            == "DISTRACTION_NOT_FOUND"
        )
        assert (
            client.delete("/sleep/999").json()["error"]["code"] == "SLEEP_LOG_NOT_FOUND"
        )
        assert (
            client.delete("/career-output/999").json()["error"]["code"]
            == "CAREER_OUTPUT_NOT_FOUND"
        )
        assert (
            client.delete("/prayers/2026-10-08/FAJR").json()["error"]["code"]
            == "PRAYER_LOG_NOT_FOUND"
        )


def test_analytics_parameter_errors_are_actionable():
    with TestClient(app) as client:
        invalid = client.get("/analytics/not-real")
        assert invalid.status_code == 400
        assert invalid.json()["error"]["code"] == "INVALID_ANALYSIS_NAME"
        invalid_range = client.get(
            "/analytics/overview?range=custom&start_date=2026-01-02&end_date=2026-01-01"
        )
        assert invalid_range.json()["error"]["code"] == "INVALID_DATE_RANGE"


def test_error_response_is_documented_for_routes():
    with TestClient(app) as client:
        schema = client.get("/openapi.json").json()
        operation = schema["paths"]["/sessions/start"]["post"]
        assert "ErrorResponse" in str(operation["responses"])
        assert "ErrorResponse" in schema["components"]["schemas"]


def test_overlap_and_future_errors_are_consistent():
    with TestClient(app) as client:
        first = client.post(
            "/sessions",
            json={
                "activity": "DSA",
                "start_time": "2020-01-01T10:00:00Z",
                "end_time": "2020-01-01T11:00:00Z",
            },
        )
        assert first.status_code == 201
        overlap = client.post(
            "/sessions",
            json={
                "activity": "PROJECT",
                "start_time": "2020-01-01T10:30:00Z",
                "end_time": "2020-01-01T11:30:00Z",
            },
        )
        assert overlap.status_code == 422
        assert overlap.json()["error"]["code"] == "OVERLAPPING_SESSION"
