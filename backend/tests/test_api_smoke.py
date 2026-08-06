import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Use a throwaway DB file for this smoke test, force demo mode
os.environ["DATABASE_URL"] = "sqlite:///./test_smoke.db"
os.environ["DEMO_MODE"] = "true"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.models.database import init_db  # noqa: E402

init_db()  # TestClient doesn't run lifespan/startup events unless used as a
# context manager; real `uvicorn` runs do trigger it normally.
client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_full_flow():
    # demo login
    r = client.post("/api/auth/demo-login")
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # create project
    r = client.post("/api/projects", json={"topic": "batch editing shorts"}, headers=headers)
    assert r.status_code == 201, r.text
    project = r.json()
    assert project["status"] == "draft"

    # list projects
    r = client.get("/api/projects", headers=headers)
    assert r.status_code == 200
    assert any(p["id"] == project["id"] for p in r.json())

    # generate pipeline
    r = client.post(f"/api/projects/{project['id']}/generate", headers=headers)
    assert r.status_code == 200, r.text
    generation = r.json()
    assert generation["version"] == 1
    assert generation["result"]["final_package"]["recommended_title"]

    # run it again -> version 2 (free version history)
    r = client.post(f"/api/projects/{project['id']}/generate", headers=headers)
    assert r.status_code == 200
    assert r.json()["version"] == 2

    # list generations, newest first
    r = client.get(f"/api/projects/{project['id']}/generations", headers=headers)
    assert r.status_code == 200
    versions = [g["version"] for g in r.json()]
    assert versions == [2, 1]

    # analytics coach standalone
    r = client.post(
        "/api/projects/analytics-coach",
        json={"ctr": "4.1%", "watch_time": "5:02", "retention_notes": "drop at 1:00", "sub_growth": "+40"},
        headers=headers,
    )
    assert r.status_code == 200, r.text
    assert "recommendations" in r.json()["output"]

    # unauthenticated request should be rejected
    r = client.get("/api/projects")
    assert r.status_code == 401

    print("ALL API SMOKE CHECKS PASSED")


if __name__ == "__main__":
    test_health()
    test_full_flow()
