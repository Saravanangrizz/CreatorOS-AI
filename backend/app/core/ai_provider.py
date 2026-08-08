"""
Model-agnostic AI provider layer.
 
Every agent talks to `AIProvider`, never to a vendor SDK directly. Switching
the whole platform from Gemini to OpenAI or Claude is a one-line env change
(AI_PROVIDER=openai) plus an API key — no code in app/agents/ changes.
 
Only GeminiProvider is fully wired to a live API today (that's the key
available for this build). OpenAIProvider / ClaudeProvider implement the
same interface with the real SDK call stubbed in a single method, so adding
a key is a copy-paste-sized change, not an architecture change.
"""
from __future__ import annotations
 
import abc
import asyncio
import json
import logging
from dataclasses import dataclass
 
from app.core.config import Settings, get_settings
 
logger = logging.getLogger(__name__)
 
 
class AIProviderError(RuntimeError):
    """Raised when the underlying model call fails or returns unusable output."""
 
 
@dataclass
class AIResponse:
    text: str
    provider: str
    model: str
 
 
class AIProvider(abc.ABC):
    name: str = "base"
 
    @abc.abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str, *, json_mode: bool = False) -> AIResponse:
        """Return a single completed response for the given prompts."""
        raise NotImplementedError
 
 
class MockProvider(AIProvider):
    """
    Deterministic, network-free provider used for demo mode, local dev
    without a key, and automated tests. Every agent still runs its real
    prompt-construction and response-parsing code against this — only the
    network call is replaced.
    """
 
    name = "mock"
 
    async def generate(self, system_prompt: str, user_prompt: str, *, json_mode: bool = False) -> AIResponse:
        await asyncio.sleep(0.05)  # simulate latency so UI loading states are exercised honestly
        payload = _mock_payload_for(system_prompt, user_prompt, json_mode)
        return AIResponse(text=payload, provider=self.name, model="mock-demo-v1")
 
 
def _safe_finish_reason(response: object) -> str:
    """Best-effort extraction of why generation stopped, for error messages
    only — never let a diagnostics lookup itself raise and mask the real error."""
    try:
        return str(response.candidates[0].finish_reason)  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        return "unknown"
 
 
class GeminiProvider(AIProvider):
    name = "gemini"
 
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise AIProviderError("GEMINI_API_KEY is not set")
        import google.generativeai as genai
 
        genai.configure(api_key=api_key)
        self._model_name = model
        self._genai = genai
 
    async def generate(self, system_prompt: str, user_prompt: str, *, json_mode: bool = False) -> AIResponse:
        generation_config: dict = {"max_output_tokens": 4096}
        if json_mode:
            generation_config["response_mime_type"] = "application/json"
 
        model = self._genai.GenerativeModel(
            model_name=self._model_name,
            system_instruction=system_prompt,
            generation_config=generation_config,
        )
        try:
            # google-generativeai's client is sync; run it off the event loop thread
            response = await asyncio.to_thread(model.generate_content, user_prompt)
        except Exception as exc:  # noqa: BLE001 - surface as our own error type
            raise AIProviderError(f"Gemini call failed: {exc}") from exc
 
        try:
            # response.text can *raise* (not just return empty) when there's
            # no valid text part — e.g. generation was cut off at
            # max_output_tokens mid-JSON, or the response was safety-filtered.
            text = response.text
        except Exception as exc:  # noqa: BLE001
            reason = _safe_finish_reason(response)
            raise AIProviderError(
                f"Gemini returned no usable text (finish_reason={reason}): {exc}"
            ) from exc
 
        if not text:
            raise AIProviderError("Gemini returned an empty response")
        return AIResponse(text=text, provider=self.name, model=self._model_name)
 
 
class OpenAIProvider(AIProvider):
    """Same interface as GeminiProvider. Wire the real openai SDK call here
    when a key is available — nothing else in the codebase needs to change."""
 
    name = "openai"
 
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise AIProviderError("OPENAI_API_KEY is not set")
        self._api_key = api_key
        self._model = model
 
    async def generate(self, system_prompt: str, user_prompt: str, *, json_mode: bool = False) -> AIResponse:
        raise AIProviderError(
            "OpenAIProvider is a ready-made stub — implement the openai SDK call here "
            "when a key is added. Interface is identical to GeminiProvider.generate()."
        )
 
 
class ClaudeProvider(AIProvider):
    """Same interface as GeminiProvider. Wire the real anthropic SDK call here
    when a key is available — nothing else in the codebase needs to change."""
 
    name = "claude"
 
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise AIProviderError("ANTHROPIC_API_KEY is not set")
        self._api_key = api_key
        self._model = model
 
    async def generate(self, system_prompt: str, user_prompt: str, *, json_mode: bool = False) -> AIResponse:
        raise AIProviderError(
            "ClaudeProvider is a ready-made stub — implement the anthropic SDK call here "
            "when a key is added. Interface is identical to GeminiProvider.generate()."
        )
 
 
def get_provider(settings: Settings | None = None) -> AIProvider:
    """Factory: reads AI_PROVIDER (or forces mock in demo mode) and returns
    the configured provider. This is the single switch point for the whole
    platform's model choice."""
    settings = settings or get_settings()
 
    if settings.demo_mode:
        return MockProvider()
 
    provider_map = {
        "gemini": lambda: GeminiProvider(settings.gemini_api_key, settings.gemini_model),
        "openai": lambda: OpenAIProvider(settings.openai_api_key, settings.openai_model),
        "claude": lambda: ClaudeProvider(settings.anthropic_api_key, settings.anthropic_model),
        "mock": lambda: MockProvider(),
    }
    factory = provider_map.get(settings.ai_provider)
    if not factory:
        raise AIProviderError(f"Unknown AI_PROVIDER '{settings.ai_provider}'")
    return factory()
 
 
# ---------------------------------------------------------------------------
# Mock payloads: realistic-shaped JSON so downstream parsing code is exercised
# the same way it would be against a real model, keyed off cheap keyword
# sniffing of the system prompt (each agent's system prompt is distinctive).
# ---------------------------------------------------------------------------
def _extract_topic(user_prompt: str) -> str:
    """Downstream agents send multi-line prompts like 'Topic: X\\nKeywords: ...'
    rather than a bare topic string. Pull just the topic so demo-mode canned
    responses stay readable instead of echoing the whole prompt back."""
    for line in user_prompt.splitlines():
        line = line.strip()
        if line.lower().startswith("topic:"):
            return line.split(":", 1)[1].strip()[:80] or "your topic"
    # First call in the chain (Trend Analyst) receives the bare topic directly
    return user_prompt.strip().splitlines()[0][:80] if user_prompt.strip() else "your topic"
 
 
def _mock_payload_for(system_prompt: str, user_prompt: str, json_mode: bool) -> str:
    sp = system_prompt.lower()
    topic = _extract_topic(user_prompt)
 
    if not json_mode:
        return f"[demo mode] Response for: {topic}"
 
    if "trend analyst" in sp:
        data = {
            "trending_angles": [
                f"'{topic}' explained in under 60 seconds",
                f"Why everyone got '{topic}' wrong",
                f"I tried '{topic}' for 30 days",
            ],
            "keywords": [topic.split()[0] if topic else "topic", "tutorial", "explained", "2026"],
            "content_gap": f"Most videos on '{topic}' skip the beginner setup step — that's your opening.",
            "reasoning": "Ranked by a mix of low competition + high evergreen search intent.",
        }
    elif "research agent" in sp:
        data = {
            "outline": [
                {"section": "Hook / problem statement", "notes": "Open with the pain point, not the solution."},
                {"section": "Core concept", "notes": "Define terms simply before going deep."},
                {"section": "Walkthrough", "notes": "Step-by-step, screen-recorded if possible."},
                {"section": "Common mistakes", "notes": "Builds trust and adds retention hook mid-video."},
                {"section": "Recap + CTA", "notes": "Summarize in one sentence, then ask for the sub."},
            ],
            "key_facts": [f"Context point relevant to {topic} #1", f"Context point relevant to {topic} #2"],
            "suggested_sources": ["Official documentation/site for the topic", "A well-known publication in this niche", "An active community forum or subreddit"],
            "reasoning": "Outline follows a proven retention curve: hook, payoff, mid-roll re-hook, close.",
        }
    elif "script writer" in sp:
        data = {
            "hook": f"Everyone's doing '{topic}' wrong — here's the 30-second fix.",
            "sections": [
                {"title": "Cold open", "script": f"[0:00] Fast-cut hook about {topic}."},
                {"title": "Body", "script": "[0:20] Main teaching content, 3 key beats."},
                {"title": "CTA", "script": "[Final 15s] Ask a question, point to sub button."},
            ],
            "cta": "Comment your biggest struggle with this below — I'll answer the top 5.",
            "reasoning": "Hook uses a contrarian claim in the first 3 seconds to fight the swipe-away.",
        }
    elif "thumbnail" in sp:
        data = {
            "concepts": [
                {"style": "Bold text + shocked face", "prompt": f"Close-up reaction shot, huge text '{topic.upper()[:40]}', red arrow"},
                {"style": "Before/after split", "prompt": f"Split-screen before/after related to '{topic}'"},
            ],
            "color_psychology": "Red/yellow for urgency and contrast against YouTube's white UI.",
            "clickability_score": 78,
            "reasoning": "High-contrast faces + 3-4 word text out-perform text-heavy thumbnails in this niche.",
        }
    elif "seo specialist" in sp:
        data = {
            "titles": [f"{topic}: The Only Guide You Need (2026)", f"I Tested {topic} So You Don't Have To"],
            "description": f"In this video I break down {topic} step by step, including the mistakes most people make.",
            "tags": [topic.split()[0] if topic else "tag", "tutorial", "how to", "2026 guide"],
            "hashtags": ["#tutorial", "#howto"],
            "chapters": [{"time": "0:00", "label": "Intro"}, {"time": "0:45", "label": "Main content"}, {"time": "8:30", "label": "Recap"}],
            "reasoning": "Titles front-load the keyword and add a specificity hook (year, personal test) to lift CTR.",
        }
    elif "publishing planner" in sp:
        data = {
            "checklist": ["Upload in 1080p+", "Add end screen", "Pin top comment", "Add to relevant playlist"],
            "best_time": "Tuesday 4:00 PM (audience timezone-adjusted)",
            "weekly_schedule": ["Mon: script + edit", "Wed: publish", "Fri: shorts cut from main video"],
            "reasoning": "Based on typical creator-audience active windows; refine with real channel analytics.",
        }
    elif "analytics coach" in sp:
        data = {
            "summary": "CTR is below channel average; retention holds well past the first 30 seconds.",
            "recommendations": [
                "Test a higher-contrast thumbnail — CTR is the current bottleneck, not retention.",
                "Move the strongest claim from 0:45 to the first 5 seconds.",
            ],
            "reasoning": "Retention shape shows the content works once clicked — the funnel leak is pre-click.",
        }
    else:
        data = {"result": f"[demo mode] generic response for {topic}"}
 
    return json.dumps(data)
