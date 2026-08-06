import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.agents.base import AgentError
from app.agents.orchestrator import Orchestrator
from app.api.deps import get_ai_provider, get_current_user
from app.core.ai_provider import AIProvider, AIProviderError
from app.models.database import SessionLocal, get_db
from app.models.models import Generation, Project, User
from app.schemas.schemas import (
    AnalyticsSnapshotIn,
    GenerationOut,
    GenerationSettings,
    ProjectCreate,
    ProjectOut,
)
from app.services import project_service

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return project_service.create_project(db, user.id, payload.topic)


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return project_service.list_projects(db, user.id)


def _get_owned_or_404(db: Session, user: User, project_id: str):
    project = project_service.get_owned_project(db, user.id, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/generate", response_model=GenerationOut)
async def generate(
    project_id: str,
    settings: GenerationSettings | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    provider: AIProvider = Depends(get_ai_provider),
):
    project = _get_owned_or_404(db, user, project_id)
    try:
        generation = await project_service.run_generation(db, project, provider, settings)
    except (AgentError, AIProviderError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return generation


@router.post("/{project_id}/generate/stream")
async def generate_stream(
    project_id: str,
    settings: GenerationSettings | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    provider: AIProvider = Depends(get_ai_provider),
):
    """Server-Sent Events version of /generate: pushes a 'stage_start' and
    'stage_done' event (with elapsed_seconds/char_count) per agent as the
    pipeline actually runs, so the frontend can show live execution
    progress instead of blocking on one response. Persists the completed
    run exactly like the non-streaming endpoint — same version-history
    behavior, just observable in real time."""
    project = _get_owned_or_404(db, user, project_id)
    project.status = "generating"
    db.add(project)
    db.commit()
    topic = project.topic  # capture plain values now — `db`/`project` are
    pid = project.id       # torn down before the generator body below runs

    orchestrator = Orchestrator(provider)

    def sse(event_type: str, payload: dict) -> str:
        return f"event: {event_type}\ndata: {json.dumps(payload)}\n\n"

    async def event_stream():
        # The `db` session injected via Depends is closed by the time this
        # generator body actually executes (FastAPI tears down dependencies
        # once the route function returns the StreamingResponse object, not
        # once the stream finishes) — open a fresh session for persistence.
        assembled: dict = {
            "topic": topic,
            "settings": (settings or GenerationSettings()).model_dump(),
            "steps": {},
            "final_package": {},
        }
        try:
            async for chunk in orchestrator.run_pipeline_streaming(topic, settings):
                if chunk["type"] == "stage_done":
                    assembled["steps"][chunk["agent"]] = chunk
                elif chunk["type"] == "final_package":
                    assembled["final_package"] = chunk["output"]
                yield sse(chunk["type"], chunk)
        except AgentError as exc:
            with SessionLocal() as fresh_db:
                fresh_project = fresh_db.get(Project, pid)
                if fresh_project:
                    fresh_project.status = "draft"
                    fresh_db.add(fresh_project)
                    fresh_db.commit()
            yield sse("error", {"detail": str(exc)})
            return

        with SessionLocal() as fresh_db:
            fresh_project = fresh_db.get(Project, pid)
            next_version = (
                fresh_db.query(func.max(Generation.version))
                .filter(Generation.project_id == pid)
                .scalar()
                or 0
            ) + 1
            generation = Generation(
                project_id=pid,
                version=next_version,
                provider=provider.name,
                result_json=json.dumps(assembled),
            )
            if fresh_project:
                fresh_project.status = "ready"
                fresh_db.add(fresh_project)
            fresh_db.add(generation)
            fresh_db.commit()
            fresh_db.refresh(generation)
            project_service.trim_generations(fresh_db, pid)
            yield sse("complete", {"generation_id": generation.id, "version": generation.version})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/{project_id}/generations", response_model=list[GenerationOut])
def generations(
    project_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _get_owned_or_404(db, user, project_id)
    return project_service.list_generations(db, project_id)


@router.post("/analytics-coach")
async def analytics_coach(
    payload: AnalyticsSnapshotIn,
    user: User = Depends(get_current_user),
    provider: AIProvider = Depends(get_ai_provider),
):
    orchestrator = Orchestrator(provider)
    try:
        result = await orchestrator.run_analytics_coach(payload.model_dump())
    except AgentError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return result
