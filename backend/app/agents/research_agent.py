from typing import Any

from app.agents.base import BaseAgent


class ResearchAgent(BaseAgent):
    key = "research_agent"
    display_name = "Research Agent"

    def system_prompt(self) -> str:
        return (
            "You are the Research Agent in CreatorOS AI. Given a topic and the "
            "Trend Analyst's chosen angle and content gap, build a structured "
            "knowledge outline a scriptwriter can work from, plus a list of "
            "reputable source names a creator should manually check for this "
            "topic (you do not have live web access, so these are suggestions "
            "to verify, not citations for facts already verified). Respond "
            "ONLY as JSON with keys: outline (array of {section, notes}), "
            "key_facts (array of strings), suggested_sources (array of source "
            "names, e.g. official sites, established publications, or "
            "well-known communities relevant to this topic), reasoning "
            "(string)."
        )

    def build_user_prompt(self, context: dict[str, Any]) -> str:
        trend = context.get("trend_analyst", {}).get("output", {})
        return (
            f"Topic: {context['topic']}\n"
            f"Chosen angle: {trend.get('trending_angles', [''])[0] if trend.get('trending_angles') else ''}\n"
            f"Content gap to address: {trend.get('content_gap', '')}"
        )
