from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any

from slugify import slugify
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.artifact import Artifact, ArtifactKind
from app.models.project import Project

logger = logging.getLogger(__name__)


def _sha256(path: Path) -> str:
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


async def create_project(session: AsyncSession, name: str) -> tuple[Project, str]:
    settings = get_settings()
    module_src = settings.specforge_module_path.resolve()
    if not module_src.is_dir():
        raise FileNotFoundError(f"SPECFORGE_MODULE_PATH not found: {module_src}")

    base_slug = slugify(name) or "project"
    slug = base_slug
    workspace = settings.workspace_root.resolve()
    workspace.mkdir(parents=True, exist_ok=True)

    counter = 1
    while (workspace / slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    project_path = workspace / slug
    project_path.mkdir(parents=True)

    dest_module = project_path / "specforge-module"
    shutil.copytree(module_src, dest_module)

    installer_output = await _run_installer(project_path, dest_module)

    project = Project(name=name, slug=slug, path=str(project_path))
    session.add(project)
    await session.commit()
    await session.refresh(project)

    await sync_artifacts(session, project)
    return project, installer_output


async def _run_installer(project_path: Path, module_path: Path) -> str:
    cmd = [
        "npx",
        "bmad-method",
        "install",
        "--directory",
        ".",
        "--modules",
        "bmm",
        "--custom-source",
        "./specforge-module",
        "--tools",
        "cursor",
        "--yes",
        "--action",
        "update",
    ]

    def run() -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            cmd,
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=600,
        )

    try:
        result = await asyncio.to_thread(run)
    except subprocess.TimeoutExpired:
        return "Installer timed out after 600s"
    except FileNotFoundError:
        return (
            "npx not found — install Node.js and run bmad-method install manually in "
            f"{project_path}"
        )

    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        output += f"\n[exit code {result.returncode}]"
    return output.strip()


async def get_project_by_slug(session: AsyncSession, slug: str) -> Project | None:
    result = await session.execute(select(Project).where(Project.slug == slug))
    return result.scalar_one_or_none()


async def sync_artifacts(session: AsyncSession, project: Project) -> list[Artifact]:
    project_path = Path(project.path)
    updated: list[Artifact] = []

    kind_map = {
        "prd": ArtifactKind.prd,
        "fsd": ArtifactKind.fsd,
        "architecture": ArtifactKind.architecture,
        "test_strategy": ArtifactKind.test_strategy,
        "last_run": ArtifactKind.last_run,
    }

    from app.services.pipeline import ARTIFACT_PATHS

    for key, rel in ARTIFACT_PATHS.items():
        full = project_path / rel
        if not full.exists():
            continue
        digest = _sha256(full)
        kind = kind_map[key]
        existing = await session.execute(
            select(Artifact).where(
                Artifact.project_id == project.id,
                Artifact.kind == kind,
            )
        )
        artifact = existing.scalar_one_or_none()
        if artifact:
            artifact.path = str(full)
            artifact.sha256 = digest
        else:
            artifact = Artifact(
                project_id=project.id,
                kind=kind,
                path=str(full),
                sha256=digest,
            )
            session.add(artifact)
        updated.append(artifact)

    await session.commit()
    return updated


def read_artifact_file(project_path: Path, kind: str) -> dict[str, Any] | None:
    from app.services.pipeline import ARTIFACT_PATHS

    rel = ARTIFACT_PATHS.get(kind)
    if not rel:
        return None
    full = project_path / rel
    if not full.exists():
        return None
    content = full.read_text(encoding="utf-8", errors="replace")
    return {
        "content": content,
        "sha256": _sha256(full),
        "updated_at": full.stat().st_mtime,
        "path": str(full),
    }


def read_last_run_json(project_path: Path) -> dict[str, Any] | None:
    path = project_path / "_bmad-output" / "specforge" / "last-run.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def parse_failures(last_run: dict[str, Any]) -> list[dict[str, str | None]]:
    failures = last_run.get("failures") or []
    items: list[dict[str, str | None]] = []
    for f in failures:
        items.append(
            {
                "fr_id": f.get("fr_id"),
                "test_name": f.get("test_id") or f.get("test_name") or "unknown",
                "message": f.get("assertion") or f.get("message") or "",
            }
        )
    return items
