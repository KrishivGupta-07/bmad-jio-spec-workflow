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

TEMPLATE_DIR_NAME = "_bmad-template"
TEMPLATE_COPY_DIRS = ("_bmad", ".agents")
PRODUCT_BRIEF_PATH = "docs/product-brief.md"

_template_lock = asyncio.Lock()
_template_build_task: asyncio.Task[None] | None = None
_template_ready = asyncio.Event()
_template_build_error: str | None = None


class TemplateNotReadyError(Exception):
    pass


def _sha256(path: Path) -> str:
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _module_hash(module_src: Path) -> str:
    digest = hashlib.sha256()
    for rel in sorted(
        [
            "module.yaml",
            "config.yaml",
            ".claude-plugin/marketplace.json",
        ]
    ):
        path = module_src / rel
        if path.is_file():
            digest.update(rel.encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def _template_path() -> Path:
    return get_settings().workspace_root.resolve() / TEMPLATE_DIR_NAME


def _template_is_current(template_path: Path, module_src: Path) -> bool:
    marker = template_path / ".specforge" / "template-ready"
    hash_file = template_path / ".specforge" / "module.sha256"
    skills = template_path / ".agents" / "skills"
    if not marker.exists() or not skills.is_dir() or not hash_file.exists():
        return False
    return hash_file.read_text(encoding="utf-8").strip() == _module_hash(module_src)


def bmad_template_status() -> dict[str, Any]:
    settings = get_settings()
    module_src = settings.specforge_module_path.resolve()
    template_path = _template_path()
    log_path = template_path / ".specforge" / "build.log"
    log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else None

    if _template_build_error:
        return {"ready": False, "running": False, "log": _template_build_error}

    building = _template_build_task is not None and not _template_build_task.done()
    ready = _template_is_current(template_path, module_src)
    return {"ready": ready, "running": building, "log": log}


def kickoff_template_build() -> None:
    """Start building the shared BMAD template once at server startup."""
    asyncio.create_task(ensure_template_ready())


async def ensure_template_ready() -> None:
    settings = get_settings()
    module_src = settings.specforge_module_path.resolve()
    if not module_src.is_dir():
        raise FileNotFoundError(f"SPECFORGE_MODULE_PATH not found: {module_src}")

    template_path = _template_path()
    if _template_is_current(template_path, module_src):
        _template_ready.set()
        return

    global _template_build_task, _template_build_error

    async with _template_lock:
        if _template_is_current(template_path, module_src):
            _template_ready.set()
            return

        if _template_build_task is None or _template_build_task.done():
            _template_ready.clear()
            _template_build_error = None
            _template_build_task = asyncio.create_task(_build_template(template_path, module_src))

    await _template_ready.wait()
    if _template_build_error:
        raise TemplateNotReadyError(_template_build_error)


def _try_bootstrap_template_from_workspace(template_path: Path, module_src: Path) -> bool:
    workspace = get_settings().workspace_root.resolve()
    if not workspace.is_dir():
        return False
    for child in sorted(workspace.iterdir()):
        if not child.is_dir() or child.name.startswith("_") or child.name.startswith("."):
            continue
        skills = child / ".agents" / "skills"
        bmad = child / "_bmad"
        if not skills.is_dir() or not bmad.is_dir():
            continue
        if template_path.exists():
            shutil.rmtree(template_path)
        template_path.mkdir(parents=True)
        for dirname in TEMPLATE_COPY_DIRS:
            shutil.copytree(child / dirname, template_path / dirname)
        shutil.copytree(module_src, template_path / "specforge-module")
        (template_path / "docs").mkdir()
        marker_dir = template_path / ".specforge"
        marker_dir.mkdir(parents=True, exist_ok=True)
        (marker_dir / "template-ready").touch()
        (marker_dir / "module.sha256").write_text(_module_hash(module_src), encoding="utf-8")
        (marker_dir / "build.log").write_text(
            f"Bootstrapped BMAD template from existing project '{child.name}'.\n",
            encoding="utf-8",
        )
        logger.info("Bootstrapped BMAD template from %s", child.name)
        return True
    return False


async def _build_template(template_path: Path, module_src: Path) -> None:
    global _template_build_error
    marker_dir = template_path / ".specforge"
    try:
        if _try_bootstrap_template_from_workspace(template_path, module_src):
            logger.info("BMAD template ready at %s (bootstrapped)", template_path)
            return

        if template_path.exists():
            shutil.rmtree(template_path)
        template_path.mkdir(parents=True)
        shutil.copytree(module_src, template_path / "specforge-module")
        (template_path / "docs").mkdir()
        output = await _run_installer(template_path, template_path / "specforge-module")
        marker_dir.mkdir(parents=True, exist_ok=True)
        (marker_dir / "template-ready").touch()
        (marker_dir / "module.sha256").write_text(_module_hash(module_src), encoding="utf-8")
        (marker_dir / "build.log").write_text(output, encoding="utf-8")
        logger.info("BMAD template ready at %s", template_path)
    except Exception as exc:
        logger.exception("BMAD template build failed")
        _template_build_error = f"BMAD template build failed: {exc}"
        marker_dir.mkdir(parents=True, exist_ok=True)
        (marker_dir / "build.log").write_text(_template_build_error, encoding="utf-8")
    finally:
        _template_ready.set()


async def _seed_project_from_template(project_path: Path, module_src: Path) -> None:
    await ensure_template_ready()
    template_path = _template_path()

    for name in TEMPLATE_COPY_DIRS:
        src = template_path / name
        dest = project_path / name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)

    dest_module = project_path / "specforge-module"
    if dest_module.exists():
        shutil.rmtree(dest_module)
    shutil.copytree(module_src, dest_module)

    (project_path / "docs").mkdir(exist_ok=True)
    (project_path / "_bmad-output").mkdir(exist_ok=True)

    marker_dir = project_path / ".specforge"
    marker_dir.mkdir(parents=True, exist_ok=True)
    (marker_dir / "bmad-install.done").touch()
    (marker_dir / "bmad-install.log").write_text(
        "Seeded from shared BMAD template.\n", encoding="utf-8"
    )


def write_product_brief(project_path: Path, description: str) -> Path:
    brief_path = project_path / PRODUCT_BRIEF_PATH
    brief_path.parent.mkdir(parents=True, exist_ok=True)
    brief_path.write_text(description.strip() + "\n", encoding="utf-8")
    return brief_path


async def create_project(
    session: AsyncSession, name: str, product_description: str
) -> tuple[Project, str]:
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

    await _seed_project_from_template(project_path, module_src)
    write_product_brief(project_path, product_description)

    project = Project(
        name=name,
        slug=slug,
        path=str(project_path),
        product_description=product_description.strip(),
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)

    return project, "Project created and ready for pipeline stages."


def bmad_install_status(project_path: Path) -> dict[str, Any]:
    log_path = project_path / ".specforge" / "bmad-install.log"
    log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else None
    skills_ready = (project_path / ".agents" / "skills").is_dir()
    return {"ready": skills_ready, "running": False, "log": log}


def require_bmad_ready(project_path: Path) -> None:
    if not (project_path / ".agents" / "skills").is_dir():
        raise ValueError(
            "BMAD modules are not installed in this project. "
            "Use retry setup on the project or create a new project."
        )


async def reseed_project(project_path: Path) -> None:
    module_src = get_settings().specforge_module_path.resolve()
    await _seed_project_from_template(project_path, module_src)


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
        raise RuntimeError(output or f"bmad-method install failed with code {result.returncode}")
    return output.strip()


async def get_project_by_slug(session: AsyncSession, slug: str) -> Project | None:
    result = await session.execute(select(Project).where(Project.slug == slug))
    return result.scalar_one_or_none()


async def update_product_description(
    session: AsyncSession, project: Project, product_description: str
) -> Project:
    description = product_description.strip()
    write_product_brief(Path(project.path), description)
    project.product_description = description
    await session.commit()
    await session.refresh(project)
    return project


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
