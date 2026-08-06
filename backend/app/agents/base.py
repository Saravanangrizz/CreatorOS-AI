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
import time
from abc import ABC, abstractmethod
from typing import Any

from app.core.ai_provider import AIProvider, AIProviderError

logger = logging.getLogger(__name__)


class AgentError(RuntimeError):
    pass


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
        try:
            response = await self.provider.generate(
                system_prompt=self.system_prompt(),
                user_prompt=user_prompt,
                json_mode=True,
            )
        except AIProviderError as exc:
            logger.error("%s failed: %s", self.display_name, exc)
            raise AgentError(f"{self.display_name} failed: {exc}") from exc
        elapsed_seconds = round(time.monotonic() - started, 2)

        try:
            parsed = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise AgentError(
                f"{self.display_name} returned non-JSON output: {exc}"
            ) from exc

        return {
            "agent": self.key,
            "display_name": self.display_name,
            "provider": response.provider,
            "model": response.model,
            "output": parsed,
            "elapsed_seconds": elapsed_seconds,
            "char_count": len(response.text),
        }
