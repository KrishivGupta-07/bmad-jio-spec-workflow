---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-streak-cli-2026-05-25/prd.md
workflowType: 'fsd'
project_name: 'Streak CLI'
user_name: 'K'
date: '2026-05-25'
lastStep: 6
status: 'complete'
completedAt: '2026-05-25'
---

# Functional Spec Document (FSD)

## Overview

Streak is a command-line habit tracker. Users create named habits, log daily completions, view per-habit streak counts, and list all habits with streak status. Data persists locally between sessions.

## Actors

| Actor | Description |
| --- | --- |
| User | A person who creates habits and logs daily completions via the CLI |

## Functional Requirements

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-001 | The system shall allow a user to create a habit with a unique non-empty name | Must |
| FR-002 | The system shall allow a user to list all habits with each habit's current streak count | Must |
| FR-003 | The system shall allow a user to log completion of a habit for today's date | Must |
| FR-004 | The system shall allow a user to view the current streak for a named habit | Must |

## User Flows

**Create habit:** User invokes create with a habit name. System validates uniqueness and non-empty name, persists the habit.

**Log completion:** User invokes done for a habit name. System records today's date as a completion; repeat logs on the same day have no effect.

**View streak:** User invokes status for a habit name. System returns consecutive-day count ending on the most recent completion day.

**List habits:** User invokes list. System returns all habits with streak counts, or an informative message when none exist.

## Acceptance Criteria

### FR-001: Create habit

**AC-001-01**

- **Given** no habit exists with the name "Morning run"
- **When** the user creates a habit named "Morning run"
- **Then** the habit is persisted and retrievable

**AC-001-02**

- **Given** a habit named "Morning run" already exists
- **When** the user attempts to create another habit named "Morning run"
- **Then** the system rejects the request with a clear error and no duplicate is created

**AC-001-03**

- **Given** the user is creating a habit
- **When** the user provides an empty name
- **Then** the system rejects the request with a clear error

### FR-002: List habits

**AC-002-01**

- **Given** two habits exist with known streak counts
- **When** the user lists all habits
- **Then** the output includes each habit name and its current streak count

**AC-002-02**

- **Given** no habits exist
- **When** the user lists all habits
- **Then** the system returns an informative message indicating no habits exist

### FR-003: Log completion

**AC-003-01**

- **Given** a habit named "Morning run" exists
- **When** the user logs completion for "Morning run" on today's date
- **Then** today's date is recorded as a completion for that habit

**AC-003-02**

- **Given** no habit named "Unknown" exists
- **When** the user attempts to log completion for "Unknown"
- **Then** the system rejects the request with a clear error

**AC-003-03**

- **Given** a habit already has a completion recorded for today
- **When** the user logs completion again for the same habit on today
- **Then** no duplicate completion is created and the operation succeeds

### FR-004: View streak

**AC-004-01**

- **Given** a habit has completions on three consecutive days ending yesterday
- **When** the user views streak for that habit
- **Then** the streak count is 3

**AC-004-02**

- **Given** a habit has a gap of one day between completions
- **When** the user views streak for that habit
- **Then** the streak count reflects only the most recent consecutive run (not the older run)

**AC-004-03**

- **Given** no habit named "Unknown" exists
- **When** the user attempts to view streak for "Unknown"
- **Then** the system rejects the request with a clear error

## Non-Functional Notes

- Commands should complete in under one second for typical local data sizes.

## Out of Scope

- Reminders, sync, accounts, habit deletion/editing, non-CLI interfaces

## Open Questions

| ID | Question | Status |
| --- | --- | --- |
| OQ-001 | Does streak include today if not yet logged today? | Resolved — streak ends on most recent completion day |
