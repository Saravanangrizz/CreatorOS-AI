from typing import Any

from app.agents.base import BaseAgent


class ThumbnailStrategistAgent(BaseAgent):
    key = "thumbnail_strategist"
    display_name = "Thumbnail Strategist"

    def system_prompt(self) -> str:
        return (
            "You are the Thumbnail Strategist agent in CreatorOS AI. Given a "
            "topic and the video's hook, propose thumbnail concepts (visual "
            "prompt + style), note the color psychology at play, and give a "
            "0-100 clickability_score. Respond ONLY as JSON with keys: "
            "concepts (array of {style, prompt}), color_psychology (string), "
            "clickability_score (integer), reasoning (string)."
        )

    def build_user_prompt(self, context: dict[str, Any]) -> str:
        script = context.get("script_writer", {}).get("output", {})
        return f"Topic: {context['topic']}\nVideo hook: {script.get('hook', '')}"
