from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models.project import Project
from app.schemas import InstallStatus, ProjectCreate, ProjectCreateResult, ProjectOut, ProjectUpdate
from app.services.artifact_watcher import start_watcher
from app.services.workspace import (
    TemplateNotReadyError,
    bmad_install_status,
    bmad_template_status,
    create_project,
    get_project_by_slug,
    reseed_project,
    update_product_description,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectOut])
async def list_projects(session: AsyncSession = Depends(get_session)) -> list[Project]:
    result = await session.execute(select(Project).order_by(Project.created_at.desc()))
    return list(result.scalars().all())


@router.get("/template/status", response_model=InstallStatus)
async def get_template_status() -> InstallStatus:
    return InstallStatus(**bmad_template_status())


@router.post("", response_model=ProjectCreateResult)
async def create_project_endpoint(
    body: ProjectCreate,
    session: AsyncSession = Depends(get_session),
) -> ProjectCreateResult:
    if not body.product_description.strip():
        raise HTTPException(status_code=400, detail="Product description cannot be empty")
    try:
        project, installer_output = await create_project(
            session, body.name, body.product_description
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except TemplateNotReadyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
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


@router.get("/{slug}/install-status", response_model=InstallStatus)
async def get_install_status(slug: str, session: AsyncSession = Depends(get_session)) -> InstallStatus:
    project = await get_project_by_slug(session, slug)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    status = bmad_install_status(Path(project.path))
    return InstallStatus(**status)


@router.post("/{slug}/retry-install", response_model=InstallStatus)
async def retry_install(slug: str, session: AsyncSession = Depends(get_session)) -> InstallStatus:
    project = await get_project_by_slug(session, slug)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        await reseed_project(Path(project.path))
    except TemplateNotReadyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    status = bmad_install_status(Path(project.path))
    return InstallStatus(**status)


@router.patch("/{slug}", response_model=ProjectOut)
async def update_project_endpoint(
    slug: str,
    body: ProjectUpdate,
    session: AsyncSession = Depends(get_session),
) -> Project:
    project = await get_project_by_slug(session, slug)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not body.product_description.strip():
        raise HTTPException(status_code=400, detail="Product description cannot be empty")
    return await update_product_description(session, project, body.product_description)
