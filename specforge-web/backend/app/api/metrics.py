from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.schemas import ProjectMetrics
from app.services.run_manager import aggregate_metrics

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/projects/{slug}", response_model=ProjectMetrics)
async def project_metrics(slug: str, session: AsyncSession = Depends(get_session)) -> ProjectMetrics:
    try:
        data = await aggregate_metrics(session, slug)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ProjectMetrics(**data)
