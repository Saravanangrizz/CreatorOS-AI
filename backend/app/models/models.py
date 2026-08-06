"""ORM models. Kept intentionally small for the hackathon scope:
User -> Projects -> Generations (one per pipeline run, versioned)."""
from __future__ import annotations

import datetime
import json
import uuid

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    display_name: Mapped[str] = mapped_column(String, default="Creator")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_utcnow)

    projects: Mapped[list["Project"]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    topic: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="draft")  # draft | generating | ready | published
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow)

    owner: Mapped["User"] = relationship(back_populates="projects")
    generations: Mapped[list["Generation"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Generation(Base):
    """One full pipeline run for a project. Stored as versioned rows so a
    project's history/version-list is just 'all generations for this
    project, newest first' — no separate versioning system needed."""

    __tablename__ = "generations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    version: Mapped[int] = mapped_column(default=1)
    provider: Mapped[str] = mapped_column(String, default="mock")
    result_json: Mapped[str] = mapped_column(Text)  # serialized orchestrator output
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_utcnow)

    project: Mapped["Project"] = relationship(back_populates="generations")

    @property
    def result(self) -> dict:
        return json.loads(self.result_json)
