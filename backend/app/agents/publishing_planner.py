from typing import Any

from app.agents.base import BaseAgent


class PublishingPlannerAgent(BaseAgent):
    key = "publishing_planner"
    display_name = "Publishing Planner"

    def system_prompt(self) -> str:
        return (
            "You are the Publishing Planner agent in CreatorOS AI. Given a "
            "topic and SEO metadata, produce an upload checklist, a "
            "recommended best publishing time, and a suggested weekly "
            "schedule. Respond ONLY as JSON with keys: checklist (array of "
            "strings), best_time (string), weekly_schedule (array of "
            "strings), reasoning (string)."
        )

    def build_user_prompt(self, context: dict[str, Any]) -> str:
        seo = context.get("seo_specialist", {}).get("output", {})
        return f"Topic: {context['topic']}\nTitle: {(seo.get('titles') or [''])[0]}"
