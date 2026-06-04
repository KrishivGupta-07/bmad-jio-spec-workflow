from __future__ import annotations

import logging
import uuid
from pathlib import Path

from app.db import async_session
from app.models.instruction import Instruction, InstructionStatus
from app.models.project import Project
from app.models.run import Run, RunStatus
from app.services.pipeline import (
    ITERATION_CAP,
    STAGE_BY_ID,
    build_prd_trigger,
)
from app.services.run_manager import _build_handoff, execute_run
from app.services.workspace import read_last_run_json, stage_completed

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


def _stage_trigger(stage_id: str, brief: str) -> str:
    """Build the trigger for a stage, prefixing the instruction brief."""
    stage = STAGE_BY_ID[stage_id]
    if stage_id == "prd":
        return build_prd_trigger(brief) if brief else stage.trigger_phrase
    base = stage.trigger_phrase
    if brief.strip():
        return f"Instructions:\n{brief}\n\n{base}".strip()
    return base


async def _create_and_execute_run(
    instruction: Instruction,
    stage_id: str,
    skill_name: str,
    trigger_phrase: str,
) -> Run:
    session_uuid = str(uuid.uuid4())
    run = Run(
        project_id=instruction.project_id,
        instruction_id=instruction.id,
        skill_name=skill_name,
        trigger_phrase=trigger_phrase,
        status=RunStatus.pending,
        claude_session_id=session_uuid,
    )
    async with async_session() as session:
        session.add(run)
        await session.commit()
        await session.refresh(run)

    # execute_run sets status to failure internally if it crashes.
    await execute_run(run.id, instruction.id, stage_id, trigger_phrase, skill_name)

    async with async_session() as session:
        run = await session.get(Run, run.id)
    return run


async def _set_instruction_status(instruction_id: int, status: InstructionStatus) -> None:
    async with async_session() as session:
        instruction = await session.get(Instruction, instruction_id)
        if instruction:
            instruction.status = status
            await session.commit()


async def run_choreography(instruction_id: int) -> None:
    """Run (or resume) the full pipeline for a single instruction.

    Stages whose outputs already exist on disk are skipped, so a partially
    completed instruction continues from where it left off instead of breaking.
    """
    async with async_session() as session:
        instruction = await session.get(Instruction, instruction_id)
        if not instruction:
            logger.error("Instruction %s not found for choreography.", instruction_id)
            return
        project = await session.get(Project, instruction.project_id)
        if not project:
            logger.error("Project for instruction %s not found.", instruction_id)
            return
        brief = (instruction.instruction_text or project.product_description or "").strip()
        base_path = Path(instruction.path)
        instr_slug = instruction.slug

    await _set_instruction_status(instruction_id, InstructionStatus.running)

    # Linear pass: run each web-UI pipeline stage in order, skipping any whose
    # artifacts already exist (resume support).
    for stage_id in LINEAR_STAGE_IDS:
        if stage_completed(base_path, stage_id):
            logger.info(
                "Skipping stage '%s' for instruction %s (%s): output already exists.",
                stage_id,
                instruction_id,
                instr_slug,
            )
            continue

        stage = STAGE_BY_ID[stage_id]
        trigger = _stage_trigger(stage_id, brief)
        async with async_session() as session:
            instruction = await session.get(Instruction, instruction_id)
        run = await _create_and_execute_run(instruction, stage_id, stage.skill_name, trigger)

        # run_tests "failure" means tests failed; don't abort, enter the fix loop.
        if run.status != RunStatus.success and stage_id != "run_tests":
            logger.error(
                "Choreography aborted: stage '%s' failed for instruction %s",
                stage_id,
                instruction_id,
            )
            await _set_instruction_status(instruction_id, InstructionStatus.failure)
            return

    # Implementation loop: patch src/ from failing tests and re-run, mirroring the
    # manual quick-dev <-> run-tests handoff (capped at ITERATION_CAP iterations).
    iteration = 1  # run_tests already executed once in the linear pass

    while iteration < ITERATION_CAP:
        last_run = read_last_run_json(base_path)
        if not last_run:
            logger.error(
                "Choreography aborted: Missing last-run.json for instruction %s",
                instruction_id,
            )
            await _set_instruction_status(instruction_id, InstructionStatus.failure)
            return

        handoff = _build_handoff(last_run)
        if not handoff:
            logger.info(
                "Choreography completed successfully for instruction %s. All tests passed.",
                instruction_id,
            )
            await _set_instruction_status(instruction_id, InstructionStatus.success)
            return

        iteration += 1
        logger.info(
            "Choreography Implementation Loop - Iteration %s for instruction %s",
            iteration,
            instruction_id,
        )

        async with async_session() as session:
            instruction = await session.get(Instruction, instruction_id)

        dev_trigger = f"Instructions:\n{brief}\n\n{handoff}"
        run = await _create_and_execute_run(
            instruction, "quick_dev", "bmad-quick-dev", dev_trigger
        )
        if run.status != RunStatus.success:
            logger.error(
                "Choreography aborted: Quick Dev failed for instruction %s at iteration %s",
                instruction_id,
                iteration,
            )
            await _set_instruction_status(instruction_id, InstructionStatus.failure)
            return

        test_trigger = _stage_trigger("run_tests", brief)
        await _create_and_execute_run(
            instruction, "run_tests", "bmad-run-tests", test_trigger
        )

    logger.warning(
        "Choreography finished for instruction %s at iteration cap with tests still failing.",
        instruction_id,
    )
    await _set_instruction_status(instruction_id, InstructionStatus.halted)
