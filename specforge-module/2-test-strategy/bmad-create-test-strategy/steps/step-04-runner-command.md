# Step 4: Environment Setup and Runner Command

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: ALWAYS read the complete step file before taking any action
- ✅ Environment Setup: one executable shell command per line (run once per environment)
- ✅ Runner Command: exactly one executable shell line (runs every iteration)
- 🚫 HALT if runner command lacks a recognized structured-output flag (see § Hard Rule)
- 📋 Select framework based on architecture stack choice
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in `{communication_language}`

## EXECUTION PROTOCOLS:

- 🎯 Derive stack from architecture document tech stack
- 💾 Write to Frameworks and Runner table, Environment Setup, and Runner Command sections
- 📖 Update frontmatter `stepsCompleted: [1, 2, 3, 4]` before loading next step

## YOUR TASK:

Select test frameworks and define environment setup commands plus the runner command the Rex agent will execute verbatim on every iteration.

## SETUP AND RUNNER PROCESS:

### 1. Identify Stack from Architecture

Extract from architecture document:

- Primary language and test framework (pytest, jest, vitest, go test, etc.)
- Existing test infrastructure if brownfield
- Structured JSON output support for the chosen framework

### 2. Populate Frameworks and Runner Table

| Level | Framework | Command |
| --- | --- | --- |
| unit | e.g. pytest | `pytest tests/unit -v` |
| integration | | |
| e2e | | |

### 3. Propose Stack Defaults (User Accepts or Overrides)

Based on the stack named in the architecture document, propose **Environment Setup** and **Runner Command** defaults below. Present both blocks; user may accept as-is or override any line.

#### Python (pytest)

**Environment Setup** (one command per line):

```
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pip install pytest-json-report
```

**Runner Command** (single line):

```
.venv/bin/python -m pytest -q --json-report --json-report-file=.specforge/pytest-report.json
```

#### Node (jest)

**Environment Setup**:

```
npm ci
```

**Runner Command**:

```
npx jest --json --outputFile=.specforge/jest-report.json
```

#### Node (vitest)

**Environment Setup**:

```
npm ci
```

**Runner Command**:

```
npx vitest run --reporter=json --outputFile=.specforge/vitest-report.json
```

#### Go

**Environment Setup**:

```
go mod download
```

**Runner Command**:

```
go test -json ./... > .specforge/gotest-report.json
```

#### Stack Not in List

If the architecture uses a stack not listed above, ask the user explicitly for:

1. **Environment Setup** — commands run once per environment (one per line)
2. **Runner Command** — single line with structured output under `.specforge/`

### 4. Write Environment Setup Section

Write commands to the **Environment Setup** section in `{output_file}`:

- One executable shell command per line inside the fenced block
- Run once per environment before any test iteration
- Prefer idempotent commands (venv create, `npm ci`, `go mod download`)
- Do not include the test runner invocation here

### 5. Write Runner Command Section

Write **one** executable shell line to the **Runner Command** section.

This command:

- Runs from `{project-root}`
- Executes the full test suite (or the agreed primary subset)
- Runs on **every** iteration (setup is separate)
- **MUST** emit structured test output to a path under `.specforge/`

### 6. Hard Rule — Structured Output (NO EXCEPTIONS)

Before saving the runner command, verify it contains at least one recognized structured-output flag:

- `--json-report`
- `--json`
- `--reporter=json`
- `-json`
- or an equivalent flag documented for the named stack

**If the user provides a runner without a recognized structured-output flag:**

- **HALT** immediately
- Do not write the runner command to the document
- Prompt the user to add the correct flag and a `.specforge/` output path
- Do not proceed until the runner passes this check

Text parsing of unstructured test output was removed deliberately. Do not weaken this rule or suggest stdout parsing as an alternative.

### 7. Populate Directory Layout

Document test directory structure mirroring `src/` per architecture.

### 8. Present to User

Show:

- Frameworks and Runner table
- Environment Setup block (all lines)
- Runner Command (single line)
- Confirm setup is idempotent where possible and runner emits JSON (or stack equivalent) under `.specforge/`

**[C] Continue to validation**

HALT — wait for [C].

## SUCCESS METRICS:

✅ Frameworks table populated for levels used
✅ Environment Setup section has one or more non-empty command lines
✅ Runner Command is exactly one executable shell line
✅ Runner command includes structured-output flag with path under `.specforge/`
✅ Directory layout documented

## NEXT STEP:

After [C], load `./step-05-validate.md`.
