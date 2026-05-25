---
title: Streak — Habit Tracker CLI
created: 2026-05-25
updated: 2026-05-25
status: final
---

# PRD: Streak — Habit Tracker CLI

## 0. Document Purpose

This PRD defines a command-line habit tracker focused on daily streaks. It is scoped for a solo developer building a personal productivity tool. Downstream workflows (FSD, architecture, test strategy) derive functional requirements from this document.

## 1. Vision

Streak is a CLI that helps people build consistency by tracking daily habit completions and showing how many consecutive days they've kept each habit alive. Users define habits once, log completion with a single command, and see streak counts that motivate continued practice.

The product prioritizes simplicity: no accounts, no sync, no GUI — just fast local commands that fit a terminal workflow.

## 2. Target User

### 2.1 Primary Persona

Alex, a developer who wants lightweight accountability for daily routines (exercise, reading, meditation) without opening a mobile app.

### 2.2 Jobs To Be Done

- Define habits I care about tracking
- Mark a habit done for today in one command
- See how many days in a row I've maintained each habit
- Review all habits and their streak status at a glance

### 2.3 Non-Users (v1)

- Teams sharing habits
- Users needing reminders/notifications
- Mobile-first users

### 2.4 Key User Journeys

- **UJ-1. Alex creates a new habit.** Alex runs `streak add "Morning run"`. The habit is saved locally and appears in future lists.
- **UJ-2. Alex logs today's completion.** Alex runs `streak done "Morning run"`. The system records today's date as completed for that habit.
- **UJ-3. Alex checks streak status.** Alex runs `streak status "Morning run"` and sees the current consecutive-day streak.
- **UJ-4. Alex reviews all habits.** Alex runs `streak list` and sees every habit with its current streak.

## 3. Glossary

- **Habit** — A named recurring activity the user wants to track. Identified by unique name.
- **Completion** — A record that the user performed a Habit on a specific calendar date.
- **Streak** — The count of consecutive calendar days (ending today or yesterday) on which a Habit was Completed without a gap.

## 4. Features

### 4.1 Habit Management

**Description:** Users create named habits stored locally. Realizes UJ-1.

**Functional Requirements:**

#### FR-1: Create habit

The user can create a Habit with a unique non-empty name. Realizes UJ-1.

**Consequences (testable):**
- A new Habit appears in storage after creation
- Duplicate names are rejected with a clear error
- Empty names are rejected

#### FR-2: List habits

The user can list all Habits with each Habit's current Streak. Realizes UJ-4.

**Consequences (testable):**
- Output includes habit name and streak count for every stored Habit
- Empty store returns an informative message (not an error)

### 4.2 Daily Logging

**Description:** Users mark habits complete for the current day. Realizes UJ-2.

**Functional Requirements:**

#### FR-3: Log completion

The user can log a Completion for a Habit for today's date. Realizes UJ-2.

**Consequences (testable):**
- Logging for an existing Habit records today's date
- Logging for unknown Habit name fails with clear error
- Logging twice on the same day is idempotent (no duplicate completion records)

### 4.3 Streak Tracking

**Description:** Users view consecutive-day streaks per habit. Realizes UJ-3.

**Functional Requirements:**

#### FR-4: View streak

The user can view the current Streak for a named Habit. Realizes UJ-3.

**Consequences (testable):**
- Streak counts consecutive days with Completions ending on the most recent completion day (today if completed today, otherwise yesterday if completed yesterday)
- A gap in days resets the streak count appropriately
- Unknown habit name fails with clear error

## 5. Success Metrics

- User can complete UJ-1 through UJ-4 in under 30 seconds total after install

## 6. Out of Scope (v1)

- Reminders and notifications
- Multi-device sync
- Habit deletion or editing
- Web or mobile UI
- User accounts

## 7. Open Questions

| ID | Question | Status |
| --- | --- | --- |
| OQ-1 | Should streak include today if not yet logged? | Resolved — streak ends on most recent completion day |
