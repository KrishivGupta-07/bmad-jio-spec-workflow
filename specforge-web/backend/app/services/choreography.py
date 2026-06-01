from __future__ import annotations

import asyncio
import logging
import uuid
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import async_session
from app.models.project import Project
from app.models.run import Run, RunStatus
from app.services.pipeline import (
    ITERATION_CAP,
    STAGE_BY_ID,
    build_prd_trigger,
)
from app.services.run_manager import _build_handoff, execute_run
from app.services.workspace import read_last_run_json

logger = logging.getLogger(__name__)

# Linear pipeline mirroring the web UI stage order (see pipeline.STAGES).
LINEAR_STAGE_IDS = [
    "prd",
    "fsd",
    "architecture",
    "test_strategy",
    "quick_dev",
    "qa_tests",
    "run_tests",
]


def _stage_trigger(stage_id: str, instructions: str, product_description: str | None) -> str:
    """Build the trigger for a stage, prefixing the auto_advance instructions."""
    stage = STAGE_BY_ID[stage_id]
    if stage_id == "prd":
        base = build_prd_trigger(product_description) if product_description else ""
    else:
        base = stage.trigger_phrase
    if instructions.strip():
        return f"Instructions:\n{instructions}\n\n{base}".strip()
    return base

async def _create_and_execute_run(
    project: Project,
    stage_id: str,
    skill_name: str,
    trigger_phrase: str,
) -> Run:
    session_uuid = str(uuid.uuid4())
    run = Run(
        project_id=project.id,
        skill_name=skill_name,
        trigger_phrase=trigger_phrase,
        status=RunStatus.pending,
        claude_session_id=session_uuid,
    )
    async with async_session() as session:
        session.add(run)
        await session.commit()
        await session.refresh(run)

    # Note: execute_run catches exceptions and sets status to failure internally if it crashes
    await execute_run(run.id, project.id, stage_id, trigger_phrase, skill_name)

    async with async_session() as session:
        run = await session.get(Run, run.id)
    return run

async def run_choreography(project_id: int, instructions: str) -> None:
    logger.info(f"Starting choreography for project {project_id} with instructions: {instructions}")

    async with async_session() as session:
        project = await session.get(Project, project_id)
        if not project:
            logger.error(f"Project {project_id} not found for choreography.")
            return

    # Linear pass: run each web-UI pipeline stage in order.
    # PRD -> FSD -> Architecture -> Test strategy -> Implement -> Generate e2e tests -> Run tests
    for stage_id in LINEAR_STAGE_IDS:
        stage = STAGE_BY_ID[stage_id]
        trigger = _stage_trigger(stage_id, instructions, project.product_description)
        run = await _create_and_execute_run(project, stage_id, stage.skill_name, trigger)

        # run_tests "failure" means tests failed; don't abort, enter the fix loop below.
        if run.status != RunStatus.success and stage_id != "run_tests":
            logger.error(
                f"Choreography aborted: stage '{stage_id}' failed for project {project_id}"
            )
            return

    # Implementation loop: patch src/ from failing tests and re-run, mirroring the
    # manual quick-dev <-> run-tests handoff (capped at ITERATION_CAP iterations).
    project_path = Path(project.path)
    iteration = 1  # run_tests already executed once in the linear pass

    while iteration < ITERATION_CAP:
        last_run = read_last_run_json(project_path)
        if not last_run:
            logger.error(f"Choreography aborted: Missing last-run.json for project {project_id}")
            return

        handoff = _build_handoff(last_run)
        if not handoff:
            logger.info(
                f"Choreography completed successfully for project {project_id}. All tests passed."
            )
            return

        iteration += 1
        logger.info(
            f"Choreography Implementation Loop - Iteration {iteration} for project {project_id}"
        )

        # Patch src/ only based on the last-run.json handoff.
        dev_trigger = f"Instructions:\n{instructions}\n\n{handoff}"
        run = await _create_and_execute_run(project, "quick_dev", "bmad-quick-dev", dev_trigger)
        if run.status != RunStatus.success:
            logger.error(
                f"Choreography aborted: Quick Dev failed for project {project_id} at iteration {iteration}"
            )
            return

        # Re-run the test suite.
        test_trigger = _stage_trigger("run_tests", instructions, project.product_description)
        await _create_and_execute_run(project, "run_tests", "bmad-run-tests", test_trigger)

    logger.warning(
        f"Choreography finished for project {project_id} at iteration cap with tests still failing."
    )
