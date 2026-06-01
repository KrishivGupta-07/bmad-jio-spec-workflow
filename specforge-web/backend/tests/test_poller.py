"""Tests for poller discovery and external project registration."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.poller import discover_external_projects


@pytest.mark.asyncio
async def test_discover_external_projects_registers_folder_with_auto_advance(tmp_path, async_session):
    scan_root = tmp_path / "scan"
    scan_root.mkdir()
    project_dir = scan_root / "my-task"
    project_dir.mkdir()
    (project_dir / "auto_advance.txt").write_text("run = false\nDo something.\n")

    with patch("app.services.poller.get_settings") as mock_settings:
        mock_settings.return_value.scan_root = scan_root
        with patch(
            "app.services.poller.register_external_project",
            new_callable=AsyncMock,
        ) as mock_register:
            await discover_external_projects(async_session)
            mock_register.assert_called_once_with(async_session, project_dir)


@pytest.mark.asyncio
async def test_discover_skips_hidden_and_underscore_dirs(tmp_path, async_session):
    scan_root = tmp_path / "scan"
    scan_root.mkdir()
    (scan_root / "_bmad-template").mkdir()
    (scan_root / ".hidden").mkdir()
    visible = scan_root / "visible"
    visible.mkdir()
    (visible / "auto_advance.txt").write_text("run = false\n")

    with patch("app.services.poller.get_settings") as mock_settings:
        mock_settings.return_value.scan_root = scan_root
        with patch(
            "app.services.poller.register_external_project",
            new_callable=AsyncMock,
        ) as mock_register:
            await discover_external_projects(async_session)
            mock_register.assert_called_once_with(async_session, visible)


@pytest.mark.asyncio
async def test_discover_noop_when_scan_root_unset(async_session, tmp_path):
    with patch("app.services.poller.get_settings") as mock_settings:
        mock_settings.return_value.scan_root = None
        mock_settings.return_value.workspace_root = tmp_path / "workspace"
        (mock_settings.return_value.workspace_root).mkdir()
        with patch(
            "app.services.poller.register_external_project",
            new_callable=AsyncMock,
        ) as mock_register:
            await discover_external_projects(async_session)
            mock_register.assert_not_called()
