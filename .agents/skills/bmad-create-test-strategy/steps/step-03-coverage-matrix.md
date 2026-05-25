# Step 3: Coverage Matrix

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: ALWAYS read the complete step file before taking any action
- ✅ EVERY FR-ID from FSD must appear in the Coverage Matrix
- 📋 Assign test levels: unit, integration, e2e, or combination
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in `{communication_language}`

## EXECUTION PROTOCOLS:

- 🎯 Process every FR-ID from the FSD inventory
- 💾 Write to test-strategy template sections
- 📖 Update frontmatter `stepsCompleted: [1, 2, 3]` before loading next step

## YOUR TASK:

Build the coverage matrix and supporting coverage sections.

## COVERAGE PROCESS:

### 1. Build Coverage Matrix

For each FR-ID from the FSD, assign at least one test level:

| FR-ID | Test Level | Notes |
| --- | --- | --- |
| FR-001 | unit / integration / e2e | Rationale for level choice |

**Level guidance:**

- **unit** — isolated logic, pure functions, single component behavior
- **integration** — component interactions, API contracts, database boundaries
- **e2e** — user-facing flows, full stack paths

A single FR may map to multiple levels when justified.

### 2. Populate Coverage Targets

Add per-module coverage targets — specific and modest:

| Module / Area | Target | Notes |
| --- | --- | --- |
| | e.g. 80% line coverage on core domain | |

Derive modules from architecture document structure.

### 3. Populate Risk-Based Priorities

Identify at least one high-risk FR with reasoning:

| FR-ID | Risk | Rationale | Priority |
| --- | --- | --- | --- |
| FR-001 | | | High |

### 4. Populate Fixtures and Test Data

Document shared fixtures, factories, and seed data strategy based on architecture.

### 5. Populate Explicitly Not Tested

List areas excluded from automated testing with rationale.

### 6. Document Test Naming Convention

Add to notes: tests should follow `test_FR_NNN_*` naming for runner FR-ID extraction.

### 7. Present to User

Show coverage matrix and targets. Ask for revisions.

**[C] Continue to runner command selection**

HALT — wait for [C].

## SUCCESS METRICS:

✅ Every FSD FR-ID has a Coverage Matrix row
✅ Coverage targets populated per module
✅ At least one risk priority with FR-ID and reasoning

## NEXT STEP:

After [C], load `./step-04-runner-command.md`.
