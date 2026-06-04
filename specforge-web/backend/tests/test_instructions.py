"""Tests for instruction creation, default adoption, and run filtering."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from app.models.project import Project
from app.models.run import Run, RunStatus
from app.services.run_manager import _instruction_run_condition
from app.services.workspace import (
    create_instruction,
    ensure_default_instruction,
    list_instructions,
)
from sqlalchemy import select


async def _make_project(session, tmp_path, name="demo"):
    project = Project(name=name, slug=name, path=str(tmp_path), product_description=None)
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


@pytest.mark.asyncio
async def test_create_instruction_makes_dir_and_row(tmp_path, async_session):
    project = await _make_project(async_session, tmp_path)

    with patch(
        "app.services.workspace._seed_project_from_template", new_callable=AsyncMock
    ):
        instr = await create_instruction(
            async_session, project, "Add a dark mode toggle to settings."
        )

    assert instr.id is not None
    assert instr.is_default is False
    assert instr.slug
    instr_dir = Path(instr.path)
    assert instr_dir.exists()
    assert instr_dir.parent.name == "instructions"
    brief = instr_dir / "docs" / "product-brief.md"
    assert brief.exists()
    assert "dark mode" in brief.read_text()


@pytest.mark.asyncio
async def test_create_instruction_unique_slugs(tmp_path, async_session):
    project = await _make_project(async_session, tmp_path)
    with patch(
        "app.services.workspace._seed_project_from_template", new_callable=AsyncMock
    ):
        a = await create_instruction(async_session, project, "Build a login page")
        b = await create_instruction(async_session, project, "Build a login page")
    assert a.slug != b.slug


@pytest.mark.asyncio
async def test_ensure_default_instruction_is_idempotent(tmp_path, async_session):
    project = await _make_project(async_session, tmp_path)
    d1 = await ensure_default_instruction(async_session, project)
    d2 = await ensure_default_instruction(async_session, project)
    assert d1.id == d2.id
    assert d1.is_default is True
    assert Path(d1.path) == tmp_path


@pytest.mark.asyncio
async def test_list_instructions_adopts_legacy_root_artifacts(tmp_path, async_session):
    project = await _make_project(async_session, tmp_path)
    # Legacy artifact at the project root, no instructions yet.
    prd = tmp_path / "_bmad-output/planning-artifacts/prds/prd-x/prd.md"
    prd.parent.mkdir(parents=True)
    prd.write_text("# PRD")

    instructions = await list_instructions(async_session, project)
    assert len(instructions) == 1
    assert instructions[0].is_default is True


@pytest.mark.asyncio
async def test_default_run_condition_includes_legacy_null_runs(tmp_path, async_session):
    project = await _make_project(async_session, tmp_path)
    default = await ensure_default_instruction(async_session, project)

    # A legacy run with no instruction_id.
    legacy = Run(
        project_id=project.id,
        instruction_id=None,
        skill_name="bmad-create-prd",
        trigger_phrase="Create PRD",
        status=RunStatus.success,
    )
    session_run = Run(
        project_id=project.id,
        instruction_id=default.id,
        skill_name="bmad-create-fsd",
        trigger_phrase="Create FSD",
        status=RunStatus.success,
    )
    async_session.add_all([legacy, session_run])
    await async_session.commit()

    rows = (
        await async_session.execute(
            select(Run).where(_instruction_run_condition(default))
        )
    ).scalars().all()
    assert {r.skill_name for r in rows} == {"bmad-create-prd", "bmad-create-fsd"}
