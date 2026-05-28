from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.schemas import RunCreate, RunDetailOut, RunOut
from app.services.pipeline import STAGE_BY_ID
from app.services.run_manager import get_run_detail, start_stage_run
from app.services.workspace import get_project_by_slug

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("", response_model=RunOut)
async def start_run(body: RunCreate, session: AsyncSession = Depends(get_session)) -> RunOut:
    if body.stage not in STAGE_BY_ID:
        raise HTTPException(status_code=400, detail=f"Unknown stage: {body.stage}")

    project = await get_project_by_slug(session, body.project_slug)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        run = await start_stage_run(session, project, body.stage)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return RunOut.model_validate(run)


@router.get("/{run_id}", response_model=RunDetailOut)
async def get_run(run_id: int, session: AsyncSession = Depends(get_session)) -> RunDetailOut:
    try:
        detail = await get_run_detail(session, run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    run = detail["run"]
    return RunDetailOut(
        **RunOut.model_validate(run).model_dump(),
        messages_count=detail["messages_count"],
        prompt_tokens=detail["prompt_tokens"],
        completion_tokens=detail["completion_tokens"],
        cost_usd=detail["cost_usd"],
        messages=detail["messages"],
        llm_calls=detail["llm_calls"],
        handoff=detail["handoff"],
        last_run=detail["last_run"],
    )
