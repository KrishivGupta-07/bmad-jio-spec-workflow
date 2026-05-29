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
from app.services.pipeline import ITERATION_CAP, STAGE_BY_ID, build_prd_trigger
from app.services.run_manager import _build_handoff, execute_run
from app.services.workspace import read_last_run_json

logger = logging.getLogger(__name__)

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

    # 1. Analysis (PRD)
    prd_trigger = build_prd_trigger(project.product_description) if project.product_description else ""
    analysis_trigger = f"Instructions:\n{instructions}\n\n{prd_trigger}".strip()
    run = await _create_and_execute_run(project, "prd", "bmad-create-prd", analysis_trigger)
    if run.status != RunStatus.success:
        logger.error(f"Choreography aborted: Analysis phase failed for project {project_id}")
        return

    # 2. Planning (Epics and Stories / fsd equivalent stage)
    planning_trigger = f"Instructions:\n{instructions}\n\nBreak requirements into epics and user stories."
    run = await _create_and_execute_run(project, "fsd", "bmad-create-epics-and-stories", planning_trigger)
    if run.status != RunStatus.success:
        logger.error(f"Choreography aborted: Planning phase failed for project {project_id}")
        return

    # 3. Solutioning (Architecture)
    solution_trigger = f"Instructions:\n{instructions}\n\nCreate architecture and technical design."
    run = await _create_and_execute_run(project, "architecture", "bmad-create-architecture", solution_trigger)
    if run.status != RunStatus.success:
        logger.error(f"Choreography aborted: Solutioning phase failed for project {project_id}")
        return

    # 4. Implementation Loop
    project_path = Path(project.path)
    iteration = 0

    while iteration < ITERATION_CAP:
        iteration += 1
        logger.info(f"Choreography Implementation Loop - Iteration {iteration} for project {project_id}")

        # QA Generation (End-to-End tests)
        qa_trigger = f"Instructions:\n{instructions}\n\nGenerate QA automated e2e tests based on the specs and architecture."
        run = await _create_and_execute_run(project, "qa_tests", "bmad-qa-generate-e2e-tests", qa_trigger)
        if run.status != RunStatus.success:
            logger.error(f"Choreography aborted: QA Generation failed for project {project_id} at iteration {iteration}")
            return

        # Run Tests
        test_trigger = f"Instructions:\n{instructions}\n\nRun the test suite."
        run = await _create_and_execute_run(project, "run_tests", "bmad-run-tests", test_trigger)
        
        # Check last-run.json to determine next steps
        last_run = read_last_run_json(project_path)
        if not last_run:
            logger.error(f"Choreography aborted: Missing last-run.json for project {project_id}")
            return

        handoff = _build_handoff(last_run)
        
        # If tests passed or there are no failures, break loop
        if not handoff:
            logger.info(f"Choreography completed successfully for project {project_id}. All tests passed.")
            break

        # If we reached the iteration cap and tests still failed, we halt
        if iteration >= ITERATION_CAP:
            logger.error(f"Choreography aborted: Iteration cap reached for project {project_id} with failing tests.")
            break

        # Otherwise, feed handoff back to Quick Dev
        dev_trigger = f"Instructions:\n{instructions}\n\n{handoff}"
        run = await _create_and_execute_run(project, "quick_dev", "bmad-quick-dev", dev_trigger)
        if run.status != RunStatus.success:
            logger.error(f"Choreography aborted: Quick Dev failed for project {project_id} at iteration {iteration}")
            return

    logger.info(f"Choreography finished for project {project_id}.")
