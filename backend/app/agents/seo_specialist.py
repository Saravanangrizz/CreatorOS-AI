from typing import Any

from app.agents.base import BaseAgent


class SEOSpecialistAgent(BaseAgent):
    key = "seo_specialist"
    display_name = "SEO Specialist"

    def system_prompt(self) -> str:
        return (
            "You are the SEO Specialist agent in CreatorOS AI. Given a topic, "
            "keywords, and the video script, produce title options, a "
            "description, tags, hashtags, and timestamped chapters. Respond "
            "ONLY as JSON with keys: titles (array of strings), description "
            "(string), tags (array of strings), hashtags (array of strings), "
            "chapters (array of {time, label}), reasoning (string explaining "
            "the SEO choices)."
        )

    def build_user_prompt(self, context: dict[str, Any]) -> str:
        trend = context.get("trend_analyst", {}).get("output", {})
        script = context.get("script_writer", {}).get("output", {})
        return (
            f"Topic: {context['topic']}\n"
            f"Keywords: {', '.join(trend.get('keywords', []))}\n"
            f"Hook: {script.get('hook', '')}"
        )
