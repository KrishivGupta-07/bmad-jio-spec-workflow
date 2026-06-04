from __future__ import annotations

import argparse
import asyncio
import logging
from decimal import Decimal

from mcp.server.fastmcp import FastMCP
from sqlalchemy import select

from app.db import async_session, init_db
from app.models.project import Project
from app.services.pipeline import ARTIFACT_KINDS, STAGE_BY_ID
from app.services.run_manager import get_run_detail, start_stage_run
from app.services.workspace import (
    create_project,
    ensure_default_instruction,
    get_project_by_slug,
    parse_failures,
    read_artifact_file,
    read_last_run_json,
)
from pathlib import Path

logger = logging.getLogger(__name__)
mcp = FastMCP("bmad")


@mcp.tool(name="bmad.list_projects")
async def list_projects() -> list[dict]:
    """List all specforge projects."""
    async with async_session() as session:
        result = await session.execute(select(Project).order_by(Project.created_at.desc()))
        return [{"slug": p.slug, "name": p.name, "path": p.path} for p in result.scalars().all()]


@mcp.tool(name="bmad.create_project")
async def create_project_tool(name: str, product_description: str) -> dict:
    """Create a new project with specforge module installed."""
    async with async_session() as session:
        project, _output = await create_project(session, name, product_description)
        return {"slug": project.slug, "path": project.path}


@mcp.tool(name="bmad.start_stage")
async def start_stage(project_slug: str, stage: str) -> dict:
    """Start a pipeline stage for a project's default instruction."""
    if stage not in STAGE_BY_ID:
        raise ValueError(f"Unknown stage: {stage}")
    async with async_session() as session:
        project = await get_project_by_slug(session, project_slug)
        if not project:
            raise ValueError(f"Project not found: {project_slug}")
        instruction = await ensure_default_instruction(session, project)
        run = await start_stage_run(session, instruction, stage)
        return {"run_id": run.id, "status": run.status.value}


@mcp.tool(name="bmad.get_run")
async def get_run(run_id: int) -> dict:
    """Get run status, token usage, and cost."""
    async with async_session() as session:
        detail = await get_run_detail(session, run_id)
        run = detail["run"]
        return {
            "status": run.status.value,
            "iteration": run.iteration,
            "messages_count": detail["messages_count"],
            "tokens": {
                "prompt": detail["prompt_tokens"],
                "completion": detail["completion_tokens"],
            },
            "cost": float(detail["cost_usd"]),
        }


@mcp.tool(name="bmad.read_artifact")
async def read_artifact(project_slug: str, kind: str) -> dict:
    """Read a planning artifact (prd|fsd|architecture|test_strategy|last_run)."""
    if kind not in ARTIFACT_KINDS:
        raise ValueError(f"Unknown kind: {kind}")
    async with async_session() as session:
        project = await get_project_by_slug(session, project_slug)
        if not project:
            raise ValueError(f"Project not found: {project_slug}")
        instruction = await ensure_default_instruction(session, project)
        data = read_artifact_file(Path(instruction.path), kind)
        if not data:
            raise ValueError(f"Artifact not found: {kind}")
        return {
            "content": data["content"],
            "sha256": data["sha256"],
            "updated_at": data["updated_at"],
        }


@mcp.tool(name="bmad.get_last_run")
async def get_last_run(project_slug: str) -> dict:
    """Return last-run.json contents for a project's default instruction."""
    async with async_session() as session:
        project = await get_project_by_slug(session, project_slug)
        if not project:
            raise ValueError(f"Project not found: {project_slug}")
        instruction = await ensure_default_instruction(session, project)
        data = read_last_run_json(Path(instruction.path))
        if not data:
            raise ValueError("last-run.json not found")
        return data


@mcp.tool(name="bmad.list_failures")
async def list_failures(project_slug: str) -> list[dict]:
    """List test failures from last-run.json (default instruction)."""
    async with async_session() as session:
        project = await get_project_by_slug(session, project_slug)
        if not project:
            raise ValueError(f"Project not found: {project_slug}")
        instruction = await ensure_default_instruction(session, project)
        data = read_last_run_json(Path(instruction.path))
        if not data:
            return []
        return parse_failures(data)


async def _ensure_db() -> None:
    await init_db()


def main() -> None:
    parser = argparse.ArgumentParser(description="specforge MCP server")
    parser.add_argument("--sse", action="store_true", help="Run with SSE transport")
    parser.add_argument("--port", type=int, default=8765, help="SSE port")
    args = parser.parse_args()

    asyncio.run(_ensure_db())

    if args.sse:
        mcp.run(transport="sse", port=args.port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
