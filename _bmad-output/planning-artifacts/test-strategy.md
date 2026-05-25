---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments:
  - _bmad-output/planning-artifacts/fsd.md
  - _bmad-output/planning-artifacts/architecture.md
workflowType: 'test-strategy'
project_name: 'Streak CLI'
user_name: 'K'
date: '2026-05-25'
lastStep: 6
status: 'complete'
completedAt: '2026-05-25'
---

# Test Strategy

## Frameworks and Runner

| Level | Framework | Command |
| --- | --- | --- |
| unit | pytest | `pytest tests/test_FR_00*.py -v` |
| integration | pytest + typer CliRunner | `pytest tests/ -v` |
| e2e | — | Out of scope (CLI-only, covered by integration) |

## Primary Runner Command

```
.venv/bin/pytest -q
```

## Directory Layout

```
tests/
  conftest.py
  test_FR_001_create_habit.py
  test_FR_002_list_habits.py
  test_FR_003_log_completion.py
  test_FR_004_view_streak.py
src/
  streak/
```

## Coverage Targets

| Module / Area | Target | Notes |
| --- | --- | --- |
| streak.py | 100% branch coverage | Streak algorithm is critical |
| service.py | 90% line coverage | All FR paths |
| cli.py | 80% line coverage | Happy path + error cases |

## Risk-Based Priorities

| FR-ID | Risk | Rationale | Priority |
| --- | --- | --- | --- |
| FR-004 | Incorrect streak after gap | Core product value; off-by-one bugs common | High |
| FR-001 | Duplicate habit corruption | Data integrity | Medium |

## Fixtures and Test Data

- `conftest.py`: `tmp_path` JSON store, `HabitService` fixture, frozen `today` via monkeypatch
- Factory helper for seeding habits with completion date lists

## Explicitly Not Tested

- Real `~/.streak/` home directory paths (use temp stores)
- Performance/load testing

## Coverage Matrix

| FR-ID | Test Level | Notes |
| --- | --- | --- |
| FR-001 | unit + integration | `test_FR_001_*` — create, duplicate, empty name |
| FR-002 | unit + integration | `test_FR_002_*` — list with data, empty store |
| FR-003 | unit + integration | `test_FR_003_*` — log, unknown habit, idempotent |
| FR-004 | unit | `test_FR_004_*` — consecutive streak, gap reset, unknown habit |

## Test Naming Convention (REQUIRED for SpecForge)

**All automated tests MUST use the naming pattern `test_FR_NNN_*` where NNN is the three-digit FR-ID from the FSD.**

Examples:
- `test_FR_001_create_habit_persists`
- `test_FR_004_streak_resets_after_gap`

The `bmad-run-tests` runner extracts `fr_id` from this pattern for dev handoff. Tests that do not follow this convention will have `fr_id: null` in failure reports.

**QA agents:** When generating tests via `bmad-qa-generate-e2e-tests`, apply this naming convention to every test function mapped to an FR-ID in the coverage matrix above.
