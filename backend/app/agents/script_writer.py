from typing import Any

from app.agents.base import BaseAgent


class ScriptWriterAgent(BaseAgent):
    key = "script_writer"
    display_name = "Script Writer"

    def system_prompt(self) -> str:
        return (
            "You are the Script Writer agent in CreatorOS AI. Given a topic and "
            "a research outline, write a retention-optimized script: a strong "
            "hook (first 3 seconds), body sections tied to the outline, and a "
            "clear call-to-action. Respond ONLY as JSON with keys: hook (string), "
            "sections (array of {title, script}), cta (string), reasoning (string "
            "explaining the retention/storytelling choices made)."
        )

    def build_user_prompt(self, context: dict[str, Any]) -> str:
        research = context.get("research_agent", {}).get("output", {})
        outline = research.get("outline", [])
        outline_text = "\n".join(f"- {o.get('section')}: {o.get('notes')}" for o in outline)
        return f"Topic: {context['topic']}\nResearch outline:\n{outline_text}"
