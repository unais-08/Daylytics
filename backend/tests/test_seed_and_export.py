from fastapi.testclient import TestClient

from app.main import app
from scripts.seed import seed_database


def test_seed_populates_every_domain_and_export_delete():
    seed_database(days=60)
    with TestClient(app) as client:
        exported = client.get("/export")
        assert exported.status_code == 200
        payload = exported.json()
        assert len(payload["work_sessions"]) >= 60
        assert (
            client.get("/analytics/overview?range=30d").json()["result"][
                "deep_work_minutes"
            ]
            > 0
        )
        assert client.delete("/data").status_code == 400
        assert client.delete("/data?confirm=true").status_code == 204
        assert all(not values for values in client.get("/export").json().values())
