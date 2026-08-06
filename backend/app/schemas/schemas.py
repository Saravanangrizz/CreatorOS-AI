from __future__ import annotations

import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr


# --- Auth ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    display_name: str = "Creator"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: EmailStr
    display_name: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Projects ---
class ProjectCreate(BaseModel):
    topic: str


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    topic: str
    status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


class GenerationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    version: int
    provider: str
    created_at: datetime.datetime
    result: dict[str, Any]


class AnalyticsSnapshotIn(BaseModel):
    ctr: str
    watch_time: str
    retention_notes: str
    sub_growth: str


# --- Generation settings (only `gemini` is functional; UI marks the rest
# "Coming Soon" per the current single-provider constraint) ---
class GenerationSettings(BaseModel):
    content_length: str = "medium"  # short | medium | long
    creativity: str = "medium"  # low | medium | high
    target_platform: str = "youtube"  # youtube | tiktok | instagram | blog
    tone: str = "professional"  # professional | educational | storytelling | humorous
    audience: str = "intermediate"  # beginner | intermediate | advanced

    def as_prompt_constraints(self) -> str:
        """Rendered once and prepended to every agent's user prompt — this
        is the single place settings become real model behavior, so adding
        a new setting never means touching all six agent files."""
        return (
            f"Generation settings — respect these constraints: "
            f"content length: {self.content_length}; "
            f"creativity level: {self.creativity}; "
            f"target platform: {self.target_platform}; "
            f"tone: {self.tone}; "
            f"target audience: {self.audience}."
        )
