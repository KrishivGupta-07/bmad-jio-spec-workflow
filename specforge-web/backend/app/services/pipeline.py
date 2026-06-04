from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Stage:
    id: str
    module: str
    skill_name: str
    trigger_phrase: str


STAGES: list[Stage] = [
    Stage("prd", "bmm", "bmad-create-prd", "Create PRD"),
    Stage("fsd", "specforge", "bmad-create-fsd", "Create FSD from my PRD"),
    Stage("architecture", "bmm", "bmad-create-architecture", "Create architecture"),
    Stage("test_strategy", "specforge", "bmad-create-test-strategy", "Create test strategy"),
    Stage("quick_dev", "bmm", "bmad-quick-dev", "Implement (quick-dev)"),
    Stage("qa_tests", "bmm", "bmad-qa-generate-e2e-tests", "Generate e2e tests"),
    Stage("run_tests", "specforge", "bmad-run-tests", "Run tests"),
]

STAGE_BY_ID: dict[str, Stage] = {s.id: s for s in STAGES}
STAGE_BY_SKILL: dict[str, Stage] = {s.skill_name: s for s in STAGES}

# Root output folder BMAD writes into, relative to the working directory it runs in.
OUTPUT_DIR = "_bmad-output"

# BMAD writes planning artifacts into nested, timestamped directories
# (e.g. _bmad-output/planning-artifacts/prds/prd-foo-2026-06-01/prd.md), and
# sometimes flat. We discover them by globbing under OUTPUT_DIR and picking the
# most recently modified match per kind.
ARTIFACT_GLOBS: dict[str, list[str]] = {
    "prd": ["**/prd.md"],
    "fsd": ["**/fsd.md"],
    "architecture": ["**/architecture.md"],
    "test_strategy": ["**/test-strategy.md", "**/test_strategy.md"],
    "last_run": ["**/last-run.json"],
}

# Valid artifact kinds (ordered) for API validation.
ARTIFACT_KINDS: list[str] = list(ARTIFACT_GLOBS.keys())

# Maps a pipeline stage to the planning artifact kind that proves it completed.
# quick_dev/qa_tests are detected via the presence of src/ and tests/ instead.
STAGE_ARTIFACT_KIND: dict[str, str] = {
    "prd": "prd",
    "fsd": "fsd",
    "architecture": "architecture",
    "test_strategy": "test_strategy",
    "run_tests": "last_run",
}

ITERATION_CAP = 5

DEV_HANDOFF_TRIGGER = (
    "Read _bmad-output/specforge/last-run.json and patch src/ only. "
    "Hard rule: never edit tests."
)


from app.services.workspace import PRODUCT_BRIEF_PATH


def build_prd_trigger(_product_description: str) -> str:
    return (
        "Create PRD (headless, intent: create). "
        f"Read the product brief at {PRODUCT_BRIEF_PATH} and use it as the primary input."
    )
