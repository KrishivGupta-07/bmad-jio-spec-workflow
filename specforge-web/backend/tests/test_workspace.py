"""Tests for external project registration."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from app.models.project import Project
from app.services.workspace import (
    get_project_by_path,
    is_bmad_installed,
    register_external_project,
)


@pytest.mark.asyncio
async def test_register_external_project_creates_db_row(tmp_path, async_session):
    project_dir = tmp_path / "my-external-task"
    project_dir.mkdir()
    (project_dir / "auto_advance.txt").write_text("run = false\n")

    with patch(
        "app.services.workspace.ensure_bmad_installed",
        new_callable=AsyncMock,
    ) as mock_install:
        with patch("app.services.artifact_watcher.start_watcher") as mock_watcher:
            project = await register_external_project(async_session, project_dir)

    assert project is not None
    assert project.name == "my-external-task"
    assert project.slug == "my-external-task"
    assert Path(project.path).resolve() == project_dir.resolve()
    mock_install.assert_called_once_with(project_dir.resolve())
    mock_watcher.assert_called_once_with(project)


@pytest.mark.asyncio
async def test_register_external_project_idempotent(tmp_path, async_session):
    project_dir = tmp_path / "repeat-me"
    project_dir.mkdir()

    async_session.add(
        Project(
            name="repeat-me",
            slug="repeat-me",
            path=str(project_dir.resolve()),
            product_description=None,
        )
    )
    await async_session.commit()

    with patch(
        "app.services.workspace.ensure_bmad_installed",
        new_callable=AsyncMock,
    ) as mock_install:
        project = await register_external_project(async_session, project_dir)

    assert project is None
    mock_install.assert_not_called()


def test_is_bmad_installed_requires_skills_and_bmad(tmp_path):
    project_dir = tmp_path / "proj"
    project_dir.mkdir()
    assert is_bmad_installed(project_dir) is False

    (project_dir / "_bmad").mkdir()
    (project_dir / ".agents" / "skills").mkdir(parents=True)
    assert is_bmad_installed(project_dir) is True


@pytest.mark.asyncio
async def test_get_project_by_path_resolves_equivalent_paths(tmp_path, async_session):
    project_dir = tmp_path / "nested" / "proj"
    project_dir.mkdir(parents=True)
    async_session.add(
        Project(
            name="proj",
            slug="proj",
            path=str(project_dir),
            product_description=None,
        )
    )
    await async_session.commit()

    found = await get_project_by_path(async_session, project_dir.resolve())
    assert found is not None
    assert found.slug == "proj"
