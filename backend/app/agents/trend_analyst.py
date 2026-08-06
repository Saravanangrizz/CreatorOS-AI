from typing import Any

from app.agents.base import BaseAgent


class TrendAnalystAgent(BaseAgent):
    key = "trend_analyst"
    display_name = "Trend Analyst"

    def system_prompt(self) -> str:
        return (
            "You are the Trend Analyst agent in CreatorOS AI, a YouTube creator "
            "operating system. Given a raw topic idea, identify high-opportunity "
            "content angles, relevant keywords, and a genuine content gap "
            "competitors are missing. Respond ONLY as JSON with keys: "
            "trending_angles (array of strings), keywords (array of strings), "
            "content_gap (string), reasoning (string explaining WHY these were chosen)."
        )

    def build_user_prompt(self, context: dict[str, Any]) -> str:
        return f"Topic: {context['topic']}"
