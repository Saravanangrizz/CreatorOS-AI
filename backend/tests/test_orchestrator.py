import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.orchestrator import Orchestrator
from app.core.ai_provider import MockProvider


async def main() -> None:
    orchestrator = Orchestrator(MockProvider())

    print("=== Full pipeline run ===")
    result = await orchestrator.run_pipeline("how to edit vlogs faster")
    for key, step in result["steps"].items():
        assert step["output"], f"{key} returned empty output"
        assert "reasoning" in step["output"], f"{key} missing reasoning field"
        assert "elapsed_seconds" in step, f"{key} missing elapsed_seconds"
        assert "char_count" in step, f"{key} missing char_count"
    print(f"Ran {len(result['steps'])} agents successfully.")
    print(json.dumps(result["final_package"], indent=2))

    print("\n=== Settings threading ===")
    from app.schemas.schemas import GenerationSettings

    custom = GenerationSettings(content_length="short", tone="humorous", target_platform="tiktok")
    settings_result = await orchestrator.run_pipeline("cooking hacks", custom)
    assert settings_result["settings"]["tone"] == "humorous"
    assert settings_result["settings"]["target_platform"] == "tiktok"
    print("Settings passed through and persisted in result:", settings_result["settings"])

    print("\n=== Streaming run ===")
    seen = []
    async for chunk in orchestrator.run_pipeline_streaming("thumbnail A/B testing"):
        seen.append(chunk.get("type") or chunk.get("agent"))
    print("Streamed order:", seen)
    assert seen.count("stage_start") == 6
    assert seen.count("stage_done") == 6
    assert seen[-1] == "final_package"

    print("\n=== Analytics coach (standalone) ===")
    coach_result = await orchestrator.run_analytics_coach(
        {"ctr": "3.2%", "watch_time": "4:12", "retention_notes": "steep drop at 0:30", "sub_growth": "+120"}
    )
    print(json.dumps(coach_result["output"], indent=2))

    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    asyncio.run(main())
