import asyncio
import sys
from pathlib import Path
from typing import Any
 
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
 
from app.agents.base import AgentError, BaseAgent  # noqa: E402
from app.core.ai_provider import AIProvider, AIProviderError, AIResponse  # noqa: E402
 
 
class ScriptedProvider(AIProvider):
    """Returns a scripted sequence of responses/exceptions, one per call —
    lets us simulate 'fails twice then succeeds' without hitting a real API."""
 
    name = "scripted"
 
    def __init__(self, script: list[str | Exception]):
        self.script = list(script)
        self.calls = 0
 
    async def generate(self, system_prompt: str, user_prompt: str, *, json_mode: bool = False) -> AIResponse:
        self.calls += 1
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return AIResponse(text=item, provider=self.name, model="scripted-v1")
 
 
class DummyAgent(BaseAgent):
    key = "dummy"
    display_name = "Dummy Agent"
 
    def system_prompt(self) -> str:
        return "dummy"
 
    def build_user_prompt(self, context: dict[str, Any]) -> str:
        return "dummy prompt"
 
 
async def test_retries_on_malformed_json_then_succeeds():
    provider = ScriptedProvider([
        "not json at all {broken",
        '{"result": "ok", "reasoning": "worked on retry"}',
    ])
    agent = DummyAgent(provider)
    result = await agent.run({})
    assert result["output"]["result"] == "ok"
    assert result["attempts"] == 2
    assert provider.calls == 2
    print("PASS: retries on malformed JSON then succeeds")
 
 
async def test_extracts_json_from_markdown_fence():
    provider = ScriptedProvider([
        '```json\n{"result": "fenced", "reasoning": "wrapped in code fence"}\n```',
    ])
    agent = DummyAgent(provider)
    result = await agent.run({})
    assert result["output"]["result"] == "fenced"
    assert result["attempts"] == 1
    print("PASS: extracts JSON from markdown fence on first attempt")
 
 
async def test_extracts_json_with_surrounding_commentary():
    provider = ScriptedProvider([
        'Sure, here is the JSON:\n{"result": "surrounded", "reasoning": "x"}\nHope that helps!',
    ])
    agent = DummyAgent(provider)
    result = await agent.run({})
    assert result["output"]["result"] == "surrounded"
    print("PASS: extracts JSON despite surrounding commentary")
 
 
async def test_raises_after_max_attempts_exhausted():
    provider = ScriptedProvider(["broken 1", "broken 2", "broken 3"])
    agent = DummyAgent(provider)
    try:
        await agent.run({})
        raise AssertionError("expected AgentError")
    except AgentError as exc:
        assert "3 attempts" in str(exc)
        assert provider.calls == 3
    print("PASS: raises AgentError after exhausting retries, not before")
 
 
async def test_provider_error_is_also_retried():
    provider = ScriptedProvider([
        AIProviderError("Gemini call failed: transient 500"),
        '{"result": "recovered", "reasoning": "x"}',
    ])
    agent = DummyAgent(provider)
    result = await agent.run({})
    assert result["output"]["result"] == "recovered"
    print("PASS: transient provider error is retried, not fatal")
 
 
async def main():
    await test_retries_on_malformed_json_then_succeeds()
    await test_extracts_json_from_markdown_fence()
    await test_extracts_json_with_surrounding_commentary()
    await test_raises_after_max_attempts_exhausted()
    await test_provider_error_is_also_retried()
    print("\nALL JSON-HARDENING CHECKS PASSED")
 
 
if __name__ == "__main__":
    asyncio.run(main())
