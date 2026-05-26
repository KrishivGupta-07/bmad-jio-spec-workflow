from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models.artifact import Artifact
from app.schemas import ArtifactOut, FailureItem, PipelineStatus, StageStatus, TestRunOut
from app.services.pipeline import ARTIFACT_PATHS
from app.services.run_manager import get_pipeline_status
from app.services.workspace import (
    get_project_by_slug,
    parse_failures,
    read_artifact_file,
    read_last_run_json,
    sync_artifacts,
)
from pathlib import Path

router = APIRouter(tags=["artifacts"])


@router.get("/projects/{slug}/artifacts", response_model=list[ArtifactOut])
async def list_artifacts(slug: str, session: AsyncSession = Depends(get_session)) -> list[ArtifactOut]:
    project = await get_project_by_slug(session, slug)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await sync_artifacts(session, project)
    result = await session.execute(
        select(Artifact).where(Artifact.project_id == project.id).order_by(Artifact.updated_at.desc())
    )
    return [ArtifactOut.model_validate(a) for a in result.scalars().all()]


@router.get("/projects/{slug}/artifacts/{kind}", response_model=ArtifactOut)
async def read_artifact(
    slug: str, kind: str, session: AsyncSession = Depends(get_session)
) -> ArtifactOut:
    if kind not in ARTIFACT_PATHS:
        raise HTTPException(status_code=400, detail=f"Unknown artifact kind: {kind}")

    project = await get_project_by_slug(session, slug)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    data = read_artifact_file(Path(project.path), kind)
    if not data:
        raise HTTPException(status_code=404, detail="Artifact not found")

    return ArtifactOut(
        id=0,
        project_id=project.id,
        kind=kind,
        path=data["path"],
        sha256=data["sha256"],
        updated_at=datetime.fromtimestamp(data["updated_at"]),
        content=data["content"],
    )


@router.get("/projects/{slug}/last-run")
async def get_last_run(slug: str, session: AsyncSession = Depends(get_session)) -> dict:
    project = await get_project_by_slug(session, slug)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    data = read_last_run_json(Path(project.path))
    if not data:
        raise HTTPException(status_code=404, detail="last-run.json not found")
    return data


@router.get("/projects/{slug}/failures", response_model=list[FailureItem])
async def list_failures(slug: str, session: AsyncSession = Depends(get_session)) -> list[FailureItem]:
    project = await get_project_by_slug(session, slug)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    data = read_last_run_json(Path(project.path))
    if not data:
        return []
    return [FailureItem(**f) for f in parse_failures(data)]


@router.get("/projects/{slug}/pipeline", response_model=PipelineStatus)
async def pipeline_status(slug: str, session: AsyncSession = Depends(get_session)) -> PipelineStatus:
    try:
        status = await get_pipeline_status(session, slug)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    stages = []
    for s in status["stages"]:
        last_run = s["last_run"]
        stages.append(
            StageStatus(
                stage_id=s["stage_id"],
                skill_name=s["skill_name"],
                module=s["module"],
                label=s["label"],
                trigger_phrase=s["trigger_phrase"],
                last_run=last_run,
                prompt_tokens=s["prompt_tokens"],
                completion_tokens=s["completion_tokens"],
                cost_usd=s["cost_usd"],
            )
        )

    latest = status["latest_test_run"]
    return PipelineStatus(
        project_slug=status["project_slug"],
        stages=stages,
        latest_test_run=TestRunOut.model_validate(latest) if latest else None,
        halt=status["halt"],
    )
