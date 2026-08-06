import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ["DATABASE_URL"] = "sqlite:///./test_sse.db"
os.environ["DEMO_MODE"] = "true"

import httpx  # noqa: E402
from asgi_lifespan import LifespanManager  # noqa: E402

from app.main import app  # noqa: E402


async def main():
    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.post("/api/auth/demo-login")
            token = r.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            r = await client.post("/api/projects", json={"topic": "SSE test topic"}, headers=headers)
            project_id = r.json()["id"]

            settings_payload = {"tone": "humorous", "target_platform": "tiktok", "content_length": "short"}

            events = []
            async with client.stream(
                "POST",
                f"/api/projects/{project_id}/generate/stream",
                headers=headers,
                json=settings_payload,
                timeout=30,
            ) as response:
                assert response.status_code == 200
                event_type = None
                async for line in response.aiter_lines():
                    if line.startswith("event:"):
                        event_type = line.split(":", 1)[1].strip()
                    elif line.startswith("data:"):
                        payload = json.loads(line.split(":", 1)[1].strip())
                        events.append((event_type, payload))
                        label = payload.get("agent", payload.get("display_name", payload.get("version", "")))
                        elapsed = payload.get("elapsed_seconds", "")
                        print(f"[{event_type}] {label} {elapsed}")

            types = [e[0] for e in events]
            assert types.count("stage_start") == 6
            assert types.count("stage_done") == 6
            assert types.count("final_package") == 1
            assert types.count("complete") == 1
            for etype, payload in events:
                if etype == "stage_done":
                    assert "elapsed_seconds" in payload
                    assert "char_count" in payload

            r = await client.get(f"/api/projects/{project_id}/generations", headers=headers)
            gens = r.json()
            assert len(gens) == 1
            assert gens[0]["result"]["settings"]["tone"] == "humorous"
            assert gens[0]["result"]["settings"]["target_platform"] == "tiktok"
            assert gens[0]["result"]["final_package"]["recommended_title"]

            print("\nALL SSE + SETTINGS CHECKS PASSED")


if __name__ == "__main__":
    asyncio.run(main())
