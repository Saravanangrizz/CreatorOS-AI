from typing import Any

from app.agents.base import BaseAgent


class AnalyticsCoachAgent(BaseAgent):
    key = "analytics_coach"
    display_name = "Analytics Coach"

    def system_prompt(self) -> str:
        return (
            "You are the Analytics Coach agent in CreatorOS AI. Given raw "
            "performance metrics (CTR, average watch time, retention curve "
            "notes, subscriber growth) for a published video, explain what "
            "they mean in plain language and recommend concrete "
            "improvements for the next upload. Respond ONLY as JSON with "
            "keys: summary (string), recommendations (array of strings), "
            "reasoning (string explaining how you diagnosed the bottleneck)."
        )

    def build_user_prompt(self, context: dict[str, Any]) -> str:
        metrics = context.get("analytics_snapshot", {})
        return (
            f"CTR: {metrics.get('ctr', 'unknown')}\n"
            f"Average watch time: {metrics.get('watch_time', 'unknown')}\n"
            f"Retention notes: {metrics.get('retention_notes', 'unknown')}\n"
            f"Subscriber growth: {metrics.get('sub_growth', 'unknown')}"
        )
