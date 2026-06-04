"""Tests for nested artifact discovery, instruction summarization, and resume."""

import json

from app.services.workspace import (
    discover_artifact_path,
    discover_artifacts,
    read_artifact_file,
    read_last_run_json,
    stage_completed,
    summarize_instruction,
)


def _write(path, content="x"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_discovers_nested_timestamped_prd(tmp_path):
    # BMAD writes PRDs into nested, timestamped directories.
    prd = tmp_path / "_bmad-output/planning-artifacts/prds/prd-demo-2026-06-01/prd.md"
    _write(prd, "# PRD")
    found = discover_artifact_path(tmp_path, "prd")
    assert found == prd

    data = read_artifact_file(tmp_path, "prd")
    assert data and data["content"] == "# PRD"


def test_discovers_flat_and_nested_for_all_kinds(tmp_path):
    _write(tmp_path / "_bmad-output/planning-artifacts/prds/prd-a-2026/prd.md")
    _write(tmp_path / "_bmad-output/planning-artifacts/fsds/fsd-a-2026/fsd.md")
    _write(tmp_path / "_bmad-output/planning-artifacts/architecture.md")
    _write(tmp_path / "_bmad-output/planning-artifacts/test-strategy.md")
    _write(tmp_path / "_bmad-output/specforge/last-run.json", json.dumps({"summary": {}}))

    found = discover_artifacts(tmp_path)
    assert set(found.keys()) == {"prd", "fsd", "architecture", "test_strategy", "last_run"}


def test_discover_picks_newest_when_multiple(tmp_path):
    older = tmp_path / "_bmad-output/planning-artifacts/prds/prd-old-2026-05-01/prd.md"
    newer = tmp_path / "_bmad-output/planning-artifacts/prds/prd-new-2026-06-01/prd.md"
    _write(older, "old")
    _write(newer, "new")
    import os
    import time

    # Force newer mtime on the "new" file.
    now = time.time()
    os.utime(older, (now - 100, now - 100))
    os.utime(newer, (now, now))

    assert discover_artifact_path(tmp_path, "prd") == newer


def test_read_last_run_json_nested(tmp_path):
    payload = {"iteration": 2, "summary": {"failed": 1}}
    _write(
        tmp_path / "_bmad-output/specforge/last-run.json",
        json.dumps(payload),
    )
    assert read_last_run_json(tmp_path) == payload


def test_stage_completed_detects_outputs(tmp_path):
    assert stage_completed(tmp_path, "prd") is False
    _write(tmp_path / "_bmad-output/planning-artifacts/prds/p/prd.md")
    assert stage_completed(tmp_path, "prd") is True

    assert stage_completed(tmp_path, "quick_dev") is False
    _write(tmp_path / "src/index.js", "console.log(1)")
    assert stage_completed(tmp_path, "quick_dev") is True

    assert stage_completed(tmp_path, "qa_tests") is False
    _write(tmp_path / "tests/test_x.py", "def test(): pass")
    assert stage_completed(tmp_path, "qa_tests") is True

    assert stage_completed(tmp_path, "run_tests") is False
    _write(tmp_path / "_bmad-output/specforge/last-run.json", "{}")
    assert stage_completed(tmp_path, "run_tests") is True


def test_summarize_instruction_makes_title_and_slug():
    title, slug = summarize_instruction(
        "Add authorization for the login page so only valid users can sign in."
    )
    assert title
    assert slug
    assert " " not in slug
    assert slug == slug.lower()


def test_summarize_instruction_handles_empty():
    title, slug = summarize_instruction("   ")
    assert title == "Untitled instruction"
    assert slug == "instruction"
