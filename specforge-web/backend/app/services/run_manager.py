from __future__ import annotations

import asyncio
import json
import logging
import uuid
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import async_session
from app.models.llm_call import LLMCall
from app.models.message import Message, MessageRole
from app.models.project import Project
from app.models.run import Run, RunStatus
from app.models.test_run import TestRun
from app.services.artifact_watcher import start_watcher
from app.services.claude_runner import (
    classify_event,
    extract_session_id,
    parse_result_usage,
    run_skill,
    _extract_text,
)
from app.services.langfuse_sink import langfuse_sink
from app.services.pipeline import (
    DEV_HANDOFF_TRIGGER,
    ITERATION_CAP,
    STAGE_BY_ID,
    STAGE_BY_SKILL,
    build_prd_trigger,
)
from app.services.workspace import read_last_run_json, require_bmad_ready, sync_artifacts

logger = logging.getLogger(__name__)


class RunEventHub:
    def __init__(self) -> None:
        self._subscribers: dict[int, set[asyncio.Queue]] = {}

    def subscribe(self, run_id: int) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._subscribers.setdefault(run_id, set()).add(q)
        return q

    def unsubscribe(self, run_id: int, q: asyncio.Queue) -> None:
        subs = self._subscribers.get(run_id)
        if subs:
            subs.discard(q)
            if not subs:
                self._subscribers.pop(run_id, None)

    async def publish(self, run_id: int, event: dict[str, Any]) -> None:
        for q in list(self._subscribers.get(run_id, set())):
            await q.put(event)


run_hub = RunEventHub()
_active_tasks: dict[int, asyncio.Task] = {}


def _build_handoff(last_run: dict[str, Any]) -> str | None:
    iteration = int(last_run.get("iteration") or 0)
    summary = last_run.get("summary") or {}
    failed = int(summary.get("failed") or 0)
    errored = int(summary.get("errored") or 0)
    exit_code = int(last_run.get("exit_code") or 0)

    if exit_code == 0 and failed == 0 and errored == 0:
        return None
    if iteration >= ITERATION_CAP:
        return (
            f"Iteration cap reached (iteration {iteration} of {ITERATION_CAP}). "
            "Halt — surface to human."
        )
    return (
        f"Tests failed at iteration {iteration}. "
        f"Invoke bmad-quick-dev (patches src/ only) — read last-run.json and patch src/ only. "
        f"Never edit tests."
    )


async def _persist_message(session: AsyncSession, run_id: int, role: MessageRole, content: str) -> Message:
    msg = Message(run_id=run_id, role=role, content=content)
    session.add(msg)
    await session.commit()
    await session.refresh(msg)
    return msg


async def execute_run(run_id: int, project_id: int, stage_id: str, trigger: str, skill_name: str) -> None:
    async with async_session() as session:
        project = await session.get(Project, project_id)
        run = await session.get(Run, run_id)
        if not project or not run:
            return

        session_uuid = run.claude_session_id or str(uuid.uuid4())
        run.claude_session_id = session_uuid
        run.status = RunStatus.running
        run.started_at = datetime.utcnow()
        await session.commit()

    trace_id = langfuse_sink.start_trace(
        run_id, skill_name, session_uuid, project.slug, run.iteration
    )

    project_path = Path(project.path)

    async def on_event(event: dict[str, Any]) -> None:
        kind, role_str, payload = classify_event(event)
        sid = extract_session_id(event)
        if sid:
            async with async_session() as s:
                r = await s.get(Run, run_id)
                if r:
                    r.claude_session_id = sid
                    await s.commit()

        if kind in ("assistant", "user", "tool_use", "tool_result", "system"):
            content = _extract_text(payload)
            msg_role = MessageRole(role_str)
            async with async_session() as s:
                msg = await _persist_message(s, run_id, msg_role, content)
                await run_hub.publish(
                    run_id,
                    {
                        "type": "message",
                        "id": msg.id,
                        "role": msg.role.value,
                        "content": msg.content,
                        "ts": msg.ts.isoformat(),
                    },
                )

        if kind == "result":
            usage = parse_result_usage(payload)
            if usage:
                async with async_session() as s:
                    call = LLMCall(
                        run_id=run_id,
                        model=usage["model"],
                        prompt_tokens=usage["prompt_tokens"],
                        completion_tokens=usage["completion_tokens"],
                        cost_usd=usage["cost_usd"],
                        latency_ms=usage.get("latency_ms"),
                        langfuse_trace_id=trace_id,
                    )
                    s.add(call)
                    await s.commit()
                langfuse_sink.log_generation(
                    run_id,
                    usage["model"],
                    usage["prompt_tokens"],
                    usage["completion_tokens"],
                    usage["cost_usd"],
                    usage.get("latency_ms"),
                )
                await run_hub.publish(
                    run_id,
                    {
                        "type": "usage",
                        "model": usage["model"],
                        "prompt_tokens": usage["prompt_tokens"],
                        "completion_tokens": usage["completion_tokens"],
                        "cost_usd": str(usage["cost_usd"]),
                    },
                )
        else:
            logger.debug("stream event: %s", kind)

    try:
        rc = await run_skill(project_path, trigger, session_uuid, on_event)
    except Exception as exc:
        logger.exception("run failed")
        async with async_session() as session:
            run = await session.get(Run, run_id)
            if run:
                run.status = RunStatus.failure
                run.ended_at = datetime.utcnow()
                await session.commit()
        await run_hub.publish(run_id, {"type": "error", "message": str(exc)})
        langfuse_sink.end_trace(run_id, "failure")
        _active_tasks.pop(run_id, None)
        return

    last_run = read_last_run_json(project_path)
    handoff: str | None = None
    final_status = RunStatus.success if rc == 0 else RunStatus.failure

    async with async_session() as session:
        run = await session.get(Run, run_id)
        project = await session.get(Project, project_id)
        if not run or not project:
            return

        if stage_id == "run_tests" and last_run:
            summary = last_run.get("summary") or {}
            iteration = int(last_run.get("iteration") or 0)
            run.iteration = iteration
            test_run = TestRun(
                project_id=project.id,
                iteration=iteration,
                passed=int(summary.get("passed") or 0),
                failed=int(summary.get("failed") or 0),
                last_run_json_path=str(
                    project_path / "_bmad-output" / "specforge" / "last-run.json"
                ),
            )
            session.add(test_run)
            handoff = _build_handoff(last_run)
            failed = int(summary.get("failed") or 0)
            errored = int(summary.get("errored") or 0)
            exit_code = int(last_run.get("exit_code") or 0)
            if exit_code != 0 or failed > 0 or errored > 0:
                final_status = RunStatus.failure
                if iteration >= ITERATION_CAP:
                    final_status = RunStatus.halted
            else:
                final_status = RunStatus.success

        run.status = final_status
        run.ended_at = datetime.utcnow()
        await session.commit()
        await sync_artifacts(session, project)

    langfuse_sink.end_trace(run_id, final_status.value)
    await run_hub.publish(
        run_id,
        {
            "type": "run_complete",
            "status": final_status.value,
            "return_code": rc,
            "handoff": handoff,
            "last_run": last_run,
        },
    )
    _active_tasks.pop(run_id, None)


async def start_stage_run(session: AsyncSession, project: Project, stage_id: str) -> Run:
    stage = STAGE_BY_ID.get(stage_id)
    if not stage:
        raise ValueError(f"Unknown stage: {stage_id}")

    trigger = stage.trigger_phrase
    if stage_id == "prd":
        if not (project.product_description or "").strip():
            raise ValueError("Product description is required before creating a PRD")
        trigger = build_prd_trigger(project.product_description)

    require_bmad_ready(Path(project.path))

    if stage_id == "quick_dev":
        last_run = read_last_run_json(Path(project.path))
        if last_run and _build_handoff(last_run):
            trigger = DEV_HANDOFF_TRIGGER

    session_uuid = str(uuid.uuid4())
    run = Run(
        project_id=project.id,
        skill_name=stage.skill_name,
        trigger_phrase=trigger,
        status=RunStatus.pending,
        claude_session_id=session_uuid,
    )
    session.add(run)
    await session.commit()
    await session.refresh(run)

    start_watcher(project)
    task = asyncio.create_task(
        execute_run(run.id, project.id, stage_id, trigger, stage.skill_name)
    )
    _active_tasks[run.id] = task
    return run


async def get_run_detail(session: AsyncSession, run_id: int) -> dict[str, Any]:
    run = await session.get(Run, run_id)
    if not run:
        raise ValueError("Run not found")

    msgs = (
        await session.execute(select(Message).where(Message.run_id == run_id).order_by(Message.ts))
    ).scalars().all()
    calls = (
        await session.execute(select(LLMCall).where(LLMCall.run_id == run_id).order_by(LLMCall.ts))
    ).scalars().all()

    prompt_tokens = sum(c.prompt_tokens for c in calls)
    completion_tokens = sum(c.completion_tokens for c in calls)
    cost_usd = sum((c.cost_usd for c in calls), Decimal("0"))

    last_run = None
    handoff = None
    if run.skill_name == STAGE_BY_ID["run_tests"].skill_name:
        project = await session.get(Project, run.project_id)
        if project:
            last_run = read_last_run_json(Path(project.path))
            if last_run:
                handoff = _build_handoff(last_run)

    return {
        "run": run,
        "messages": msgs,
        "llm_calls": calls,
        "messages_count": len(msgs),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "cost_usd": cost_usd,
        "handoff": handoff,
        "last_run": last_run,
    }


async def aggregate_metrics(session: AsyncSession, project_slug: str) -> dict[str, Any]:
    project = (
        await session.execute(select(Project).where(Project.slug == project_slug))
    ).scalar_one_or_none()
    if not project:
        raise ValueError("Project not found")

    runs = (
        await session.execute(select(Run).where(Run.project_id == project.id))
    ).scalars().all()
    run_ids = [r.id for r in runs]

    if not run_ids:
        return {
            "project_slug": project_slug,
            "total_runs": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "cost_usd": Decimal("0"),
            "runs_by_stage": {},
        }

    agg = await session.execute(
        select(
            func.coalesce(func.sum(LLMCall.prompt_tokens), 0),
            func.coalesce(func.sum(LLMCall.completion_tokens), 0),
            func.coalesce(func.sum(LLMCall.cost_usd), 0),
        ).where(LLMCall.run_id.in_(run_ids))
    )
    row = agg.one()

    runs_by_stage: dict[str, int] = {}
    for r in runs:
        runs_by_stage[r.skill_name] = runs_by_stage.get(r.skill_name, 0) + 1

    return {
        "project_slug": project_slug,
        "total_runs": len(runs),
        "prompt_tokens": int(row[0]),
        "completion_tokens": int(row[1]),
        "cost_usd": row[2] or Decimal("0"),
        "runs_by_stage": runs_by_stage,
    }


async def get_pipeline_status(session: AsyncSession, project_slug: str) -> dict[str, Any]:
    from app.services.pipeline import STAGES

    project = (
        await session.execute(select(Project).where(Project.slug == project_slug))
    ).scalar_one_or_none()
    if not project:
        raise ValueError("Project not found")

    latest_test = (
        await session.execute(
            select(TestRun)
            .where(TestRun.project_id == project.id)
            .order_by(TestRun.ts.desc())
            .limit(1)
        )
    ).scalar_one_or_none()

    halt = False
    if latest_test and latest_test.iteration >= ITERATION_CAP and latest_test.failed > 0:
        halt = True

    stages_out = []
    for stage in STAGES:
        last_run_row = (
            await session.execute(
                select(Run)
                .where(Run.project_id == project.id, Run.skill_name == stage.skill_name)
                .order_by(Run.started_at.desc().nullslast())
                .limit(1)
            )
        ).scalar_one_or_none()

        stage_run_ids = (
            await session.execute(
                select(Run.id).where(
                    Run.project_id == project.id, Run.skill_name == stage.skill_name
                )
            )
        ).scalars().all()

        pt, ct, cost = 0, 0, Decimal("0")
        if stage_run_ids:
            agg = await session.execute(
                select(
                    func.coalesce(func.sum(LLMCall.prompt_tokens), 0),
                    func.coalesce(func.sum(LLMCall.completion_tokens), 0),
                    func.coalesce(func.sum(LLMCall.cost_usd), 0),
                ).where(LLMCall.run_id.in_(stage_run_ids))
            )
            a = agg.one()
            pt, ct, cost = int(a[0]), int(a[1]), a[2] or Decimal("0")

        stages_out.append(
            {
                "stage_id": stage.id,
                "skill_name": stage.skill_name,
                "module": stage.module,
                "label": stage.trigger_phrase,
                "trigger_phrase": stage.trigger_phrase,
                "last_run": last_run_row,
                "prompt_tokens": pt,
                "completion_tokens": ct,
                "cost_usd": cost,
            }
        )

    return {
        "project_slug": project_slug,
        "stages": stages_out,
        "latest_test_run": latest_test,
        "halt": halt,
    }
