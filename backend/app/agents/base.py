"""
Shared agent contract. Every specialized agent (Trend Analyst, Research Agent,
Script Writer, Thumbnail Strategist, SEO Specialist, Publishing Planner,
Analytics Coach) subclasses this and only needs to supply its system prompt
and how it turns pipeline context into a user prompt. All AI-calling and
JSON-parsing logic lives here once, not duplicated seven times.
"""
from __future__ import annotations

import json
import logging
import re
import time
from abc import ABC, abstractmethod
from typing import Any

from app.core.ai_provider import AIProvider, AIProviderError

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3  # 1 initial call + 2 retries — real models occasionally
# return malformed JSON (truncation, a stray unescaped quote); a same-prompt
# retry succeeds the overwhelming majority of the time, and it's far cheaper
# than failing a 6-agent pipeline on the last stage.

_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE | re.MULTILINE)


class AgentError(RuntimeError):
    pass


def _parse_json_response(text: str) -> dict[str, Any]:
    """Best-effort JSON parse. Real model output occasionally isn't clean
    JSON even when explicitly asked for it — this handles the two most
    common real-world cases (markdown code fences around the JSON, and
    leading/trailing commentary outside the JSON object) before giving up
    and letting the caller retry the whole generation."""
    stripped = _FENCE_RE.sub("", text.strip()).strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    # Fallback: slice from the first '{' to the last '}' — catches cases
    # where the model added a sentence before/after the JSON object.
    start, end = stripped.find("{"), stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(stripped[start : end + 1])
        except json.JSONDecodeError:
            pass

    raise json.JSONDecodeError("Could not extract valid JSON", stripped, 0)


class BaseAgent(ABC):
    #: short machine name, used as the key in the orchestrator's context dict
    key: str
    #: human label shown in the UI ("Trend Analyst", etc.)
    display_name: str

    def __init__(self, provider: AIProvider):
        self.provider = provider

    @abstractmethod
    def system_prompt(self) -> str:
        """Defines this agent's role. Must be distinctive enough for the
        MockProvider's keyword sniffing to route to the right canned payload
        in demo mode — keep the agent's display_name / role phrase in here."""
        raise NotImplementedError

    @abstractmethod
    def build_user_prompt(self, context: dict[str, Any]) -> str:
        """Turn the accumulated pipeline context (topic + prior agents'
        outputs) into this agent's input prompt."""
        raise NotImplementedError

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        user_prompt = self.build_user_prompt(context)
        # Generation settings (content length, tone, platform, etc.) are
        # rendered once by the orchestrator and stashed in context; every
        # agent picks them up here automatically, no per-agent wiring needed.
        settings_text = context.get("_settings_text")
        if settings_text:
            user_prompt = f"{settings_text}\n\n{user_prompt}"

        started = time.monotonic()
        last_error: Exception | None = None

        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = await self.provider.generate(
                    system_prompt=self.system_prompt(),
                    user_prompt=user_prompt,
                    json_mode=True,
                )
            except AIProviderError as exc:
                last_error = exc
                logger.warning(
                    "%s call failed (attempt %d/%d): %s",
                    self.display_name, attempt, MAX_ATTEMPTS, exc,
                )
                continue

            try:
                parsed = _parse_json_response(response.text)
            except json.JSONDecodeError as exc:
                last_error = exc
                logger.warning(
                    "%s returned unparseable JSON (attempt %d/%d): %s",
                    self.display_name, attempt, MAX_ATTEMPTS, exc,
                )
                continue

            elapsed_seconds = round(time.monotonic() - started, 2)
            return {
                "agent": self.key,
                "display_name": self.display_name,
                "provider": response.provider,
                "model": response.model,
                "output": parsed,
                "elapsed_seconds": elapsed_seconds,
                "char_count": len(response.text),
                "attempts": attempt,
            }

        logger.error("%s failed after %d attempts: %s", self.display_name, MAX_ATTEMPTS, last_error)
        raise AgentError(
            f"{self.display_name} failed after {MAX_ATTEMPTS} attempts: {last_error}"
        )
