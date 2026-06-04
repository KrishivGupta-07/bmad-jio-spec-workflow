from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models.artifact import Artifact
from app.models.instruction import Instruction
from app.models.project import Project
from app.schemas import (
    ArtifactOut,
    FailureItem,
    InstructionDetailOut,
    InstructionOut,
    PipelineStatus,
    ProjectMetrics,
    RunOut,
    StageStart,
    StageStatus,
    TestRunOut,
)
from app.services.choreography import run_choreography
from app.services.pipeline import ARTIFACT_KINDS, STAGE_BY_ID
from app.services.run_manager import (
    aggregate_metrics,
    get_pipeline_status,
    start_stage_run,
)
from app.services.workspace import (
    parse_failures,
    read_artifact_file,
    read_last_run_json,
    sync_artifacts,
)

router = APIRouter(prefix="/instructions", tags=["instructions"])


async def _get_instruction(session: AsyncSession, instruction_id: int) -> Instruction:
    instruction = await session.get(Instruction, instruction_id)
    if not instruction:
        raise HTTPException(status_code=404, detail="Instruction not found")
    return instruction


def _instruction_dump(instruction: Instruction) -> dict:
    return InstructionOut.model_validate(instruction).model_dump()


@router.get("/{instruction_id}", response_model=InstructionDetailOut)
async def get_instruction(
    instruction_id: int, session: AsyncSession = Depends(get_session)
) -> InstructionDetailOut:
    instruction = await _get_instruction(session, instruction_id)
    project = await session.get(Project, instruction.project_id)
    return InstructionDetailOut(
        **_instruction_dump(instruction),
        project_slug=project.slug if project else "",
        project_name=project.name if project else "",
    )


@router.get("/{instruction_id}/pipeline", response_model=PipelineStatus)
async def instruction_pipeline(
    instruction_id: int, session: AsyncSession = Depends(get_session)
) -> PipelineStatus:
    instruction = await _get_instruction(session, instruction_id)
    status = await get_pipeline_status(session, instruction)

    stages = [
        StageStatus(
            stage_id=s["stage_id"],
            skill_name=s["skill_name"],
            module=s["module"],
            label=s["label"],
            trigger_phrase=s["trigger_phrase"],
            last_run=s["last_run"],
            prompt_tokens=s["prompt_tokens"],
            completion_tokens=s["completion_tokens"],
            cost_usd=s["cost_usd"],
        )
        for s in status["stages"]
    ]
    latest = status["latest_test_run"]
    return PipelineStatus(
        project_slug=status["project_slug"],
        instruction_id=instruction.id,
        stages=stages,
        latest_test_run=TestRunOut.model_validate(latest) if latest else None,
        halt=status["halt"],
    )


@router.get("/{instruction_id}/metrics", response_model=ProjectMetrics)
async def instruction_metrics(
    instruction_id: int, session: AsyncSession = Depends(get_session)
) -> ProjectMetrics:
    instruction = await _get_instruction(session, instruction_id)
    data = await aggregate_metrics(session, instruction)
    return ProjectMetrics(**data)


@router.get("/{instruction_id}/artifacts", response_model=list[ArtifactOut])
async def list_instruction_artifacts(
    instruction_id: int, session: AsyncSession = Depends(get_session)
) -> list[ArtifactOut]:
    instruction = await _get_instruction(session, instruction_id)
    project = await session.get(Project, instruction.project_id)
    if project:
        await sync_artifacts(session, project, instruction)
    result = await session.execute(
        select(Artifact)
        .where(Artifact.instruction_id == instruction.id)
        .order_by(Artifact.updated_at.desc())
    )
    return [ArtifactOut.model_validate(a) for a in result.scalars().all()]


@router.get("/{instruction_id}/artifacts/{kind}", response_model=ArtifactOut)
async def read_instruction_artifact(
    instruction_id: int, kind: str, session: AsyncSession = Depends(get_session)
) -> ArtifactOut:
    if kind not in ARTIFACT_KINDS:
        raise HTTPException(status_code=400, detail=f"Unknown artifact kind: {kind}")
    instruction = await _get_instruction(session, instruction_id)
    data = read_artifact_file(Path(instruction.path), kind)
    if not data:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return ArtifactOut(
        id=0,
        project_id=instruction.project_id,
        instruction_id=instruction.id,
        kind=kind,
        path=data["path"],
        sha256=data["sha256"],
        updated_at=datetime.fromtimestamp(data["updated_at"]),
        content=data["content"],
    )


@router.get("/{instruction_id}/last-run")
async def instruction_last_run(
    instruction_id: int, session: AsyncSession = Depends(get_session)
) -> dict:
    instruction = await _get_instruction(session, instruction_id)
    data = read_last_run_json(Path(instruction.path))
    if not data:
        raise HTTPException(status_code=404, detail="last-run.json not found")
    return data


@router.get("/{instruction_id}/failures", response_model=list[FailureItem])
async def instruction_failures(
    instruction_id: int, session: AsyncSession = Depends(get_session)
) -> list[FailureItem]:
    instruction = await _get_instruction(session, instruction_id)
    data = read_last_run_json(Path(instruction.path))
    if not data:
        return []
    return [FailureItem(**f) for f in parse_failures(data)]


@router.post("/{instruction_id}/runs", response_model=RunOut)
async def start_instruction_run(
    instruction_id: int,
    body: StageStart,
    session: AsyncSession = Depends(get_session),
) -> RunOut:
    if body.stage not in STAGE_BY_ID:
        raise HTTPException(status_code=400, detail=f"Unknown stage: {body.stage}")
    instruction = await _get_instruction(session, instruction_id)
    try:
        run = await start_stage_run(session, instruction, body.stage)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return RunOut.model_validate(run)


@router.post("/{instruction_id}/advance", response_model=InstructionDetailOut)
async def advance_instruction(
    instruction_id: int, session: AsyncSession = Depends(get_session)
) -> InstructionDetailOut:
    """Start or resume the full choreography for this instruction."""
    instruction = await _get_instruction(session, instruction_id)
    project = await session.get(Project, instruction.project_id)
    asyncio.create_task(run_choreography(instruction.id))
    return InstructionDetailOut(
        **_instruction_dump(instruction),
        project_slug=project.slug if project else "",
        project_name=project.name if project else "",
    )
