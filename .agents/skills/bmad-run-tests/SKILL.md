---
name: bmad-run-tests
description: 'Execute test strategy runner command, parse failures, write last-run.json, and decide green/handoff/halt. Use when the user says "run tests" or invokes the test execution loop.'
---

# Run Tests Workflow

**Goal:** Execute the primary runner command from test-strategy.md, write structured results to last-run.json, and decide green completion, dev handoff, or loop-cap halt (5-iteration maximum).

**Your Role:** You are a deterministic test execution orchestrator. You run commands, parse output, write reports, and emit handoff instructions. You do NOT edit source code, tests, or documentation.

## Conventions

- Bare paths (e.g. `steps/step-01-init.md`) resolve from the skill root.
- `{skill-root}` resolves to this skill's installed directory (where `customize.toml` lives).
- `{project-root}`-prefixed paths resolve from the project working directory.
- `{skill-name}` resolves to the skill directory's basename.

## Input Files

| Input | Location | Load Mode |
| --- | --- | --- |
| test_strategy | `{planning_artifacts}/test-strategy.md` | FULL_LOAD |
| last_run | `{specforge_artifacts}/last-run.json` | optional — used for iteration counter |

## Output

| Output | Location |
| --- | --- |
| last-run report | `{specforge_artifacts}/last-run.json` |

## WORKFLOW ARCHITECTURE

### Core Principles

- **Micro-file Design**: Each step is a self-contained instruction file
- **Just-In-Time Loading**: Only the current step file is loaded
- **Sequential Enforcement**: Complete steps in order; no skipping
- **Deterministic Execution**: Run commands verbatim; no creative interpretation
- **Loop Cap**: 5-iteration maximum enforced in step-05-decide-loop

### Critical Rules (NO EXCEPTIONS)

- 🛑 **NEVER** edit `src/`, tests, or docs
- 📖 **ALWAYS** read entire step file before execution
- 🚫 **NEVER** auto-invoke other workflows — emit handoff for user
- 💾 **ONLY** step-04-write-report writes `last-run.json`
- ⛔ **HALT** at iteration >= 5 with failures — no dev handoff

## On Activation

### Step 1: Resolve the Workflow Block

Run: `python3 {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --key workflow`

**If the script fails**, resolve the `workflow` block yourself by reading these three files in base → team → user order and applying the same structural merge rules as the resolver:

1. `{skill-root}/customize.toml` — defaults
2. `{project-root}/_bmad/custom/{skill-name}.toml` — team overrides
3. `{project-root}/_bmad/custom/{skill-name}.user.toml` — personal overrides

Any missing file is skipped. Scalars override, tables deep-merge, arrays of tables keyed by `code` or `id` replace matching entries and append new entries, and all other arrays append.

### Step 2: Execute Prepend Steps

Execute each entry in `{workflow.activation_steps_prepend}` in order before proceeding.

### Step 3: Load Persistent Facts

Treat every entry in `{workflow.persistent_facts}` as foundational context. Entries prefixed `file:` are paths or globs under `{project-root}` — load the referenced contents as facts. All other entries are facts verbatim.

### Step 4: Load Config

Load config from `{project-root}/_bmad/specforge/config.yaml` and resolve:

- Use `{user_name}` for greeting
- Use `{communication_language}` for all communications
- Use `{planning_artifacts}` for test-strategy location
- Use `{specforge_artifacts}` for last-run.json output

### Step 5: Greet the User

Greet `{user_name}`, speaking in `{communication_language}`.

### Step 6: Execute Append Steps

Execute each entry in `{workflow.activation_steps_append}` in order.

Activation is complete. Begin the workflow below.

## Execution

Read fully and follow: `./steps/step-01-init.md` to begin the workflow.
