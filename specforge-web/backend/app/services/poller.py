import asyncio
import logging
from pathlib import Path

import aiofiles
import aiofiles.os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import async_session
from app.models.project import Project
from app.services.choreography import run_choreography
from app.services.workspace import register_external_project

logger = logging.getLogger(__name__)

# Tracks running choreography tasks by project ID
active_choreographies: dict[int, asyncio.Task] = {}

async def _check_and_start_choreography(project: Project) -> None:
    if project.id in active_choreographies:
        return

    workspace_path = Path(project.path)
    file_path = workspace_path / "auto_advance.txt"
    temp_path = workspace_path / "auto_advance.txt.tmp"

    if not await aiofiles.os.path.exists(file_path):
        return

    try:
        async with aiofiles.open(file_path, "r") as f:
            content = await f.read()

        lines = content.splitlines()
        if not lines:
            return

        first_line = lines[0].strip().replace(" ", "").lower()
        if first_line != "run=true":
            return

        # Rewrite to run = false atomically using a temp file
        instructions = "\n".join(lines[1:])
        async with aiofiles.open(temp_path, "w") as f:
            await f.write(f"run = false\n{instructions}")
        
        await aiofiles.os.replace(temp_path, file_path)

        # Start choreography
        logger.info(f"Triggering choreography for project {project.id}")
        task = asyncio.create_task(run_choreography(project.id, instructions))
        active_choreographies[project.id] = task

        # Add done callback to clear the guard
        task.add_done_callback(lambda t: active_choreographies.pop(project.id, None))

    except Exception as e:
        logger.error(f"Error checking auto_advance.txt for project {project.id}: {e}")


async def discover_external_projects(session: AsyncSession) -> None:
    settings = get_settings()
    scan_root = (settings.scan_root or settings.workspace_root).resolve()
    if not scan_root.is_dir():
        logger.warning("SCAN_ROOT is not a directory: %s", scan_root)
        return

    for child in sorted(scan_root.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith(".") or child.name.startswith("_"):
            continue
        auto_advance = child / "auto_advance.txt"
        if not auto_advance.exists():
            continue
        try:
            await register_external_project(session, child)
        except Exception as e:
            logger.error("Failed to register external project %s: %s", child, e)


async def start_polling() -> None:
    settings = get_settings()
    interval = getattr(settings, "poll_interval_seconds", 600)
    
    logger.info(f"Starting auto-advance poller with interval {interval}s")

    while True:
        try:
            async with async_session() as session:
                await discover_external_projects(session)
                projects = (await session.execute(select(Project))).scalars().all()
                
            for project in projects:
                await _check_and_start_choreography(project)
                
        except asyncio.CancelledError:
            logger.info("Poller task cancelled.")
            break
        except Exception as e:
            logger.error(f"Error in poller loop: {e}")

        try:
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            logger.info("Poller task cancelled during sleep.")
            break
