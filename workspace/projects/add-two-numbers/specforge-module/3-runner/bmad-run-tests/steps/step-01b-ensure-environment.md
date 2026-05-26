# Step 1b: Ensure Environment

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER edit src/, tests, docs, or test-strategy.md
- 📖 CRITICAL: Read complete step file before acting
- ✅ Run setup commands sequentially from project root — blocking, one at a time
- 🚫 env-ready marker is the ONLY skip mechanism — no .venv, node_modules, or timestamp heuristics
- 🚫 Setup failure is a HARD halt — never proceed to step-02 on non-zero exit
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in `{communication_language}`

## EXECUTION PROTOCOLS:

- 🎯 Read **Environment Setup** from `{planning_artifacts}/test-strategy.md`
- 💾 Write `.specforge/env-ready` only after all setup commands succeed
- 🔐 Compare `test_strategy_hash` (sha256 of full test-strategy.md) before skipping setup
- 🚫 FORBIDDEN to execute test runner commands in this step

## YOUR TASK:

Ensure the test environment is prepared once per environment (or re-prepared when test-strategy.md changes) before any test execution.

## ENVIRONMENT SETUP SEQUENCE:

### 1. Load Environment Setup Section

Read `{planning_artifacts}/test-strategy.md` in full.

Extract the **Environment Setup** section: all non-blank executable shell lines inside its fenced code block (one command per line).

**If section missing or fenced block empty:**

> Environment Setup is missing or empty in `{planning_artifacts}/test-strategy.md`. Run `bmad-create-test-strategy` (step-04) to define setup commands before running tests.

**HALT** — do not load step-02.

### 2. Compute Test Strategy Hash

Compute sha256 (hex digest) of the **entire** current `test-strategy.md` file content (raw bytes as read from disk).

Store as `{{test_strategy_hash}}`.

### 3. Check env-ready Marker

Marker path: `{project-root}/.specforge/env-ready`

**If file exists:**

- Parse YAML contents
- Read `test_strategy_hash` field
- **If** stored hash equals `{{test_strategy_hash}}` → skip setup (proceed to §6)
- **If** hash differs → run setup (§4) — strategy changed; setup must re-run

**If file missing:**

→ run setup (§4)

### 4. Run Setup Commands (Sequential)

From `{project-root}`, execute each setup command **one at a time**, in listed order:

```bash
cd {project-root} && <command>
```

For each command capture:

- stdout (full)
- stderr (full)
- exit code

**If any command exits non-zero:**

> SETUP HALT — command failed: `<command>`
> Exit code: `<code>`
> Last 40 lines of output:
> ```
> <last 40 lines of combined stdout+stderr>
> ```

**HALT** — do not load step-02. Do not write or update env-ready.

### 5. Write env-ready Marker

On all commands succeeding, write `.specforge/env-ready`:

```yaml
timestamp: <ISO-8601 UTC>
test_strategy_hash: <sha256 hex>
commands_executed:
  - <command 1>
  - <command 2>
  - ...
```

Use the exact commands that ran (verbatim from Environment Setup section).

### 6. Report Status

Report to user:

- Skipped setup (hash match) **or** setup completed (commands run)
- `{{test_strategy_hash}}` (abbreviated ok)
- env-ready path

## HALT CONDITIONS

- **HALT** — Environment Setup section missing or empty in test-strategy.md
- **HALT** — any setup command exits non-zero (include command, exit code, last 40 output lines)
- **HALT** — do not proceed to step-02 under any halt condition above

## SUCCESS METRICS:

✅ Environment Setup section present with at least one command
✅ test-strategy.md sha256 computed
✅ env-ready exists with matching hash (skip path) **or** all setup commands succeeded and env-ready written
✅ Ready to execute tests in step-02

## FAILURE METRICS:

❌ test-strategy.md missing Environment Setup → halted before step-02
❌ setup command non-zero exit → halted before step-02; env-ready not updated
❌ attempted to infer skip from .venv, node_modules, or timestamps instead of env-ready hash

## NEXT STEP:

Load `./step-02-execute.md`.
