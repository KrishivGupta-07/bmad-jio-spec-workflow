from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models.llm_call import LLMCall
from app.models.project import Project
from app.models.run import Run
from app.schemas import ProjectMetrics

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/projects/{slug}", response_model=ProjectMetrics)
async def project_metrics(slug: str, session: AsyncSession = Depends(get_session)) -> ProjectMetrics:
    project = (
        await session.execute(select(Project).where(Project.slug == slug))
    ).scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    runs = (
        await session.execute(select(Run).where(Run.project_id == project.id))
    ).scalars().all()
    run_ids = [r.id for r in runs]

    runs_by_stage: dict[str, int] = {}
    for r in runs:
        runs_by_stage[r.skill_name] = runs_by_stage.get(r.skill_name, 0) + 1

    pt, ct, cost = 0, 0, Decimal("0")
    if run_ids:
        agg = await session.execute(
            select(
                func.coalesce(func.sum(LLMCall.prompt_tokens), 0),
                func.coalesce(func.sum(LLMCall.completion_tokens), 0),
                func.coalesce(func.sum(LLMCall.cost_usd), 0),
            ).where(LLMCall.run_id.in_(run_ids))
        )
        row = agg.one()
        pt, ct, cost = int(row[0]), int(row[1]), row[2] or Decimal("0")

    return ProjectMetrics(
        project_slug=slug,
        total_runs=len(runs),
        prompt_tokens=pt,
        completion_tokens=ct,
        cost_usd=cost,
        runs_by_stage=runs_by_stage,
    )
