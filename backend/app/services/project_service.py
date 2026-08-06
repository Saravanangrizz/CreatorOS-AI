"""Business logic for projects and generations. Routes stay thin and only
translate HTTP <-> this layer, per the 'no business logic in routes' rule."""
from __future__ import annotations

import json

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.agents.orchestrator import Orchestrator
from app.core.ai_provider import AIProvider
from app.models.models import Generation, Project
from app.schemas.schemas import GenerationSettings

MAX_GENERATIONS_PER_PROJECT = 5


def create_project(db: Session, owner_id: str, topic: str) -> Project:
    project = Project(owner_id=owner_id, topic=topic, status="draft")
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def list_projects(db: Session, owner_id: str) -> list[Project]:
    return (
        db.query(Project)
        .filter(Project.owner_id == owner_id)
        .order_by(Project.updated_at.desc())
        .all()
    )


def get_owned_project(db: Session, owner_id: str, project_id: str) -> Project | None:
    return (
        db.query(Project)
        .filter(Project.id == project_id, Project.owner_id == owner_id)
        .first()
    )


def trim_generations(db: Session, project_id: str, keep: int = MAX_GENERATIONS_PER_PROJECT) -> None:
    """Keep only the most recent `keep` generations for a project — bounds
    storage growth while still giving free version history/comparison for
    the versions that matter most (the recent ones)."""
    stale = (
        db.query(Generation)
        .filter(Generation.project_id == project_id)
        .order_by(Generation.version.desc())
        .offset(keep)
        .all()
    )
    for gen in stale:
        db.delete(gen)
    if stale:
        db.commit()


async def run_generation(
    db: Session,
    project: Project,
    provider: AIProvider,
    settings: GenerationSettings | None = None,
) -> Generation:
    """Runs the full agent pipeline for a project and stores the result as
    a new version — every generation is kept (up to MAX_GENERATIONS_PER_PROJECT),
    giving free version history."""
    project.status = "generating"
    db.add(project)
    db.commit()

    orchestrator = Orchestrator(provider)
    try:
        result = await orchestrator.run_pipeline(project.topic, settings)
    except Exception:
        project.status = "draft"
        db.add(project)
        db.commit()
        raise

    next_version = (
        db.query(func.max(Generation.version))
        .filter(Generation.project_id == project.id)
        .scalar()
        or 0
    ) + 1
    generation = Generation(
        project_id=project.id,
        version=next_version,
        provider=provider.name,
        result_json=json.dumps(result),
    )
    project.status = "ready"
    db.add_all([generation, project])
    db.commit()
    db.refresh(generation)
    trim_generations(db, project.id)
    return generation


def list_generations(db: Session, project_id: str) -> list[Generation]:
    return (
        db.query(Generation)
        .filter(Generation.project_id == project_id)
        .order_by(Generation.version.desc())
        .all()
    )
