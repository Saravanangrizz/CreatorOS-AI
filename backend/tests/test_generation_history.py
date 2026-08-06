import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ["DATABASE_URL"] = "sqlite:///./test_history.db"
os.environ["DEMO_MODE"] = "true"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.models.database import init_db  # noqa: E402

init_db()
client = TestClient(app)


def test_generation_history_trims_and_versions_correctly():
    r = client.post("/api/auth/demo-login")
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post("/api/projects", json={"topic": "history trim test"}, headers=headers)
    project_id = r.json()["id"]

    versions_seen = []
    for _ in range(7):
        r = client.post(f"/api/projects/{project_id}/generate", headers=headers)
        assert r.status_code == 200, r.text
        versions_seen.append(r.json()["version"])

    # versions must strictly increase, never repeat, even after trimming kicks in
    assert versions_seen == [1, 2, 3, 4, 5, 6, 7], versions_seen

    r = client.get(f"/api/projects/{project_id}/generations", headers=headers)
    stored = r.json()
    assert len(stored) == 5, f"expected 5 kept, got {len(stored)}"
    kept_versions = sorted(g["version"] for g in stored)
    assert kept_versions == [3, 4, 5, 6, 7], kept_versions

    print("ALL GENERATION HISTORY CHECKS PASSED")


if __name__ == "__main__":
    test_generation_history_trims_and_versions_correctly()
