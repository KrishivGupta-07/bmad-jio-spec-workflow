from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.schemas import RunDetailOut, RunOut
from app.services.run_manager import get_run_detail

router = APIRouter(prefix="/runs", tags=["runs"])


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
        auth_error=detail["auth_error"],
    )
