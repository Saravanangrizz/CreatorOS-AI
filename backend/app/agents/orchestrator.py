"""
Central AI Orchestrator.

Runs the specialized agents in sequence, feeding each agent the accumulated
context (topic + every prior agent's output) so later agents can build on
earlier ones — e.g. the Script Writer sees the Research Agent's outline, the
SEO Specialist sees the script's hook. This is the "agents collaborating on
one workflow" differentiator, not isolated single-shot prompts.

This module has zero HTTP/route concerns — it's pure orchestration logic so
it's independently unit-testable (see backend/tests/test_orchestrator.py).
"""
from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from typing import Any

from app.agents.analytics_coach import AnalyticsCoachAgent
from app.agents.base import AgentError, BaseAgent
from app.agents.publishing_planner import PublishingPlannerAgent
from app.agents.research_agent import ResearchAgent
from app.agents.script_writer import ScriptWriterAgent
from app.agents.seo_specialist import SEOSpecialistAgent
from app.agents.thumbnail_strategist import ThumbnailStrategistAgent
from app.agents.trend_analyst import TrendAnalystAgent
from app.core.ai_provider import AIProvider
from app.schemas.schemas import GenerationSettings

logger = logging.getLogger(__name__)

# Order matters: this is the creator-workflow pipeline from idea to publish.
# Analytics Coach is intentionally excluded — it runs on-demand against a
# published video's metrics, not as part of the idea->publish chain.
PIPELINE: list[type[BaseAgent]] = [
    TrendAnalystAgent,
    ResearchAgent,
    ScriptWriterAgent,
    ThumbnailStrategistAgent,
    SEOSpecialistAgent,
    PublishingPlannerAgent,
]


class Orchestrator:
    def __init__(self, provider: AIProvider):
        self.provider = provider
        self._pipeline_agents = [cls(provider) for cls in PIPELINE]
        self._analytics_agent = AnalyticsCoachAgent(provider)

    async def run_pipeline(
        self, topic: str, settings: GenerationSettings | None = None
    ) -> dict[str, Any]:
        """Run the full idea->publish pipeline for a topic, returning every
        agent's output plus a 'final_package' summary view."""
        context: dict[str, Any] = self._init_context(topic, settings)

        for agent in self._pipeline_agents:
            try:
                result = await agent.run(context)
            except AgentError as exc:
                logger.error("Pipeline halted at %s: %s", agent.display_name, exc)
                raise
            context[agent.key] = result

        return {
            "topic": topic,
            "settings": (settings or GenerationSettings()).model_dump(),
            "steps": {agent_cls.key: context[agent_cls.key] for agent_cls in PIPELINE},
            "final_package": self._assemble_final_package(context),
        }

    async def run_pipeline_streaming(
        self, topic: str, settings: GenerationSettings | None = None
    ) -> AsyncIterator[dict[str, Any]]:
        """Same pipeline, but yields a 'stage_start' event before each agent
        runs and a 'stage_done' event (including elapsed_seconds/char_count)
        right after — this drives the UI's live execution view instead of
        one blocking response."""
        context: dict[str, Any] = self._init_context(topic, settings)
        for agent in self._pipeline_agents:
            yield {"type": "stage_start", "agent": agent.key, "display_name": agent.display_name}
            result = await agent.run(context)
            context[agent.key] = result
            yield {"type": "stage_done", **result}
        yield {"type": "final_package", "output": self._assemble_final_package(context)}

    async def run_analytics_coach(self, analytics_snapshot: dict[str, Any]) -> dict[str, Any]:
        context = {"analytics_snapshot": analytics_snapshot}
        return await self._analytics_agent.run(context)

    @staticmethod
    def _init_context(topic: str, settings: GenerationSettings | None) -> dict[str, Any]:
        settings = settings or GenerationSettings()
        return {"topic": topic, "_settings_text": settings.as_prompt_constraints()}

    @staticmethod
    def _assemble_final_package(context: dict[str, Any]) -> dict[str, Any]:
        """Flatten the pipeline's outputs into the ready-to-publish asset
        bundle a creator actually walks away with."""
        seo = context.get("seo_specialist", {}).get("output", {})
        script = context.get("script_writer", {}).get("output", {})
        thumb = context.get("thumbnail_strategist", {}).get("output", {})
        publish = context.get("publishing_planner", {}).get("output", {})

        return {
            "recommended_title": (seo.get("titles") or [""])[0],
            "hook": script.get("hook", ""),
            "description": seo.get("description", ""),
            "tags": seo.get("tags", []),
            "hashtags": seo.get("hashtags", []),
            "chapters": seo.get("chapters", []),
            "thumbnail_concepts": thumb.get("concepts", []),
            "publishing_checklist": publish.get("checklist", []),
            "best_publish_time": publish.get("best_time", ""),
        }
