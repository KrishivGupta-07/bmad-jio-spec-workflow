from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models.project import Project
from app.schemas import (
    InstallStatus,
    InstructionCreate,
    InstructionOut,
    ProjectCreate,
    ProjectCreateResult,
    ProjectOut,
    ProjectUpdate,
)
from app.services.artifact_watcher import start_watcher
from app.services.choreography import run_choreography
from app.services.workspace import (
    TemplateNotReadyError,
    bmad_install_status,
    bmad_template_status,
    create_instruction,
    create_project,
    get_project_by_slug,
    list_instructions,
    require_bmad_ready,
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
    if not body.name.strip():
        raise HTTPException(status_code=400, detail="Project name cannot be empty")
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


@router.get("/{slug}/instructions", response_model=list[InstructionOut])
async def list_project_instructions(
    slug: str, session: AsyncSession = Depends(get_session)
) -> list[InstructionOut]:
    project = await get_project_by_slug(session, slug)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    instructions = await list_instructions(session, project)
    return [InstructionOut.model_validate(i) for i in instructions]


@router.post("/{slug}/instructions", response_model=InstructionOut)
async def create_project_instruction(
    slug: str,
    body: InstructionCreate,
    session: AsyncSession = Depends(get_session),
) -> InstructionOut:
    project = await get_project_by_slug(session, slug)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="Instruction text cannot be empty")
    try:
        require_bmad_ready(Path(project.path))
        instruction = await create_instruction(session, project, body.text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    start_watcher(project)
    # Kick off the full pipeline for this instruction in the background, exactly
    # like an armed auto_advance.txt would.
    asyncio.create_task(run_choreography(instruction.id))
    return InstructionOut.model_validate(instruction)


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
