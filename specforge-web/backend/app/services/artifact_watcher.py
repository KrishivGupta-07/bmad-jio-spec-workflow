from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from watchfiles import awatch

from app.db import async_session
from app.models.project import Project
from app.services.workspace import list_instructions, sync_artifacts
from sqlalchemy import select

logger = logging.getLogger(__name__)

_watch_tasks: dict[int, asyncio.Task] = {}


async def watch_project_artifacts(project: Project) -> None:
    project_path = Path(project.path)
    project_path.mkdir(parents=True, exist_ok=True)
    # Watch the whole project so per-instruction output dirs are covered too.
    (project_path / "_bmad-output").mkdir(parents=True, exist_ok=True)

    async for changes in awatch(project_path):
        logger.debug("artifact change %s: %s", project.slug, changes)
        async with async_session() as session:
            result = await session.execute(select(Project).where(Project.id == project.id))
            db_project = result.scalar_one_or_none()
            if not db_project:
                continue
            for instruction in await list_instructions(session, db_project):
                await sync_artifacts(session, db_project, instruction)


def start_watcher(project: Project) -> None:
    if project.id in _watch_tasks:
        return
    task = asyncio.create_task(watch_project_artifacts(project))
    _watch_tasks[project.id] = task


def stop_watcher(project_id: int) -> None:
    task = _watch_tasks.pop(project_id, None)
    if task:
        task.cancel()
