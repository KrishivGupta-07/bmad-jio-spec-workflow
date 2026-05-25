---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-streak-cli-2026-05-25/prd.md
  - _bmad-output/planning-artifacts/fsd.md
workflowType: 'architecture'
project_name: 'Streak CLI'
user_name: 'K'
date: '2026-05-25'
lastStep: 8
status: 'complete'
completedAt: '2026-05-25'
---

# Architecture Decision Document

## Project Context

Streak is a local-first Python CLI for habit tracking with daily streak calculation. No network, no database server — JSON file persistence on disk. Target user runs commands from terminal; data file lives in a configurable path (default: `~/.streak/habits.json`).

## Starter Template Decision

**Greenfield Python CLI** — no starter template. Standard `src/` layout with `pyproject.toml`, Typer for CLI, pytest for tests.

## Core Architectural Decisions

### Language & Runtime

| Decision | Choice | Rationale |
| --- | --- | --- |
| Language | Python 3.10+ | Simple CLI, strong datetime/stdlib support |
| CLI framework | Typer | Typed commands, good UX, argparse-compatible |
| Persistence | JSON file | Matches solo/local scope; human-readable |
| Date handling | `datetime.date` (ISO strings in JSON) | Calendar-day streak semantics |

### Data Model

```python
# Conceptual schema (habits.json)
{
  "habits": {
    "Morning run": {
      "completions": ["2026-05-23", "2026-05-24", "2026-05-25"]
    }
  }
}
```

- Habit names are unique keys (case-sensitive)
- Completions stored as sorted unique ISO date strings
- Streak computed at read time from completion list

### Streak Algorithm

1. Sort completion dates descending
2. If empty → streak = 0
3. Anchor on most recent completion date
4. Walk backward day-by-day while consecutive dates exist in set
5. Return count

### Error Handling

- Domain errors raise `HabitError` with user-facing message
- CLI catches and prints to stderr, exit code 1

## Implementation Patterns

- **Layered modules:** `cli` → `service` → `store` + `streak`
- **Dependency injection:** `HabitService(store: HabitStore)` for testability
- **Store interface:** `HabitStore` protocol with `JsonHabitStore` implementation
- **No global state** in domain logic

## Project Structure & Boundaries

```
streak-cli/
├── pyproject.toml
├── README.md
├── src/
│   └── streak/
│       ├── __init__.py
│       ├── __main__.py      # python -m streak entry
│       ├── cli.py           # Typer commands: add, done, status, list
│       ├── models.py        # Habit, Completion dataclasses
│       ├── store.py         # JsonHabitStore read/write
│       ├── service.py       # HabitService business logic
│       ├── streak.py        # compute_streak(dates, today) -> int
│       └── errors.py        # HabitError
└── tests/
    ├── conftest.py          # tmp_path store fixtures
    ├── test_FR_001_create_habit.py
    ├── test_FR_002_list_habits.py
    ├── test_FR_003_log_completion.py
    └── test_FR_004_view_streak.py
```

### Requirements to Structure Mapping

| FR-ID | Module |
| --- | --- |
| FR-001 | `service.py` (create_habit), `cli.py` (add command) |
| FR-002 | `service.py` (list_habits), `cli.py` (list command) |
| FR-003 | `service.py` (log_completion), `cli.py` (done command) |
| FR-004 | `streak.py`, `service.py` (get_streak), `cli.py` (status command) |

### CLI Commands

| Command | Maps to |
| --- | --- |
| `streak add NAME` | FR-001 |
| `streak list` | FR-002 |
| `streak done NAME` | FR-003 |
| `streak status NAME` | FR-004 |

## Testing Strategy (Architecture)

- **Framework:** pytest
- **Unit tests:** domain (`streak.py`, `service.py`) with in-memory/temp JSON store
- **CLI tests:** `typer.testing.CliRunner` for command integration
- **Naming:** `test_FR_NNN_*` per SpecForge runner convention

## Validation

Architecture supports all four FSD requirements with clear module boundaries, testable streak logic, and local JSON persistence. No external dependencies beyond Typer.
