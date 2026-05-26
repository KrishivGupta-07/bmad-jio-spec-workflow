from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models.project import Project
from app.schemas import ProjectCreate, ProjectCreateResult, ProjectOut
from app.services.artifact_watcher import start_watcher
from app.services.workspace import create_project

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectOut])
async def list_projects(session: AsyncSession = Depends(get_session)) -> list[Project]:
    result = await session.execute(select(Project).order_by(Project.created_at.desc()))
    return list(result.scalars().all())


@router.post("", response_model=ProjectCreateResult)
async def create_project_endpoint(
    body: ProjectCreate,
    session: AsyncSession = Depends(get_session),
) -> ProjectCreateResult:
    try:
        project, installer_output = await create_project(session, body.name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    start_watcher(project)
    return ProjectCreateResult(
        project=ProjectOut.model_validate(project),
        installer_output=installer_output,
    )


@router.get("/{slug}", response_model=ProjectOut)
async def get_project(slug: str, session: AsyncSession = Depends(get_session)) -> Project:
    result = await session.execute(select(Project).where(Project.slug == slug))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
