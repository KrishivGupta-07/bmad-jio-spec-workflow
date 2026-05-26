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

ARTIFACT_PATHS: dict[str, str] = {
    "prd": "_bmad-output/planning-artifacts/prd.md",
    "fsd": "_bmad-output/planning-artifacts/fsd.md",
    "architecture": "_bmad-output/planning-artifacts/architecture.md",
    "test_strategy": "_bmad-output/planning-artifacts/test-strategy.md",
    "last_run": "_bmad-output/specforge/last-run.json",
}

ITERATION_CAP = 5

DEV_HANDOFF_TRIGGER = (
    "Read _bmad-output/specforge/last-run.json and patch src/ only. "
    "Hard rule: never edit tests."
)
