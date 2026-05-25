# Step 4: Runner Command

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: ALWAYS read the complete step file before taking any action
- ✅ Primary runner command must be a single executable shell line
- 📋 Select framework based on architecture stack choice
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in `{communication_language}`

## EXECUTION PROTOCOLS:

- 🎯 Derive framework from architecture document tech stack
- 💾 Write to Frameworks and Runner table and Primary Runner Command section
- 📖 Update frontmatter `stepsCompleted: [1, 2, 3, 4]` before loading next step

## YOUR TASK:

Select test frameworks and define the primary runner command the Rex agent will execute verbatim.

## RUNNER SELECTION PROCESS:

### 1. Identify Stack from Architecture

Extract from architecture document:

- Primary language and test framework (pytest, jest, vitest, go test, etc.)
- Existing test infrastructure if brownfield
- Structured output support (JSON reporters)

### 2. Populate Frameworks and Runner Table

| Level | Framework | Command |
| --- | --- | --- |
| unit | e.g. pytest | `pytest tests/unit -v` |
| integration | | |
| e2e | | |

### 3. Define Primary Runner Command

Write **one** executable shell line to the **Primary Runner Command** section.

This command:

- Runs from `{project-root}`
- Executes the full test suite (or the agreed primary subset)
- Prefers structured JSON output when available:
  - pytest: `--json-report --json-report-file={specforge_artifacts}/pytest-report.json`
  - jest: `--json --outputFile={specforge_artifacts}/jest-report.json`
  - vitest: `--reporter=json --outputFile={specforge_artifacts}/vitest-report.json`
- Is copy-pasteable without modification by the runner agent

Example:

```
pytest tests/ -v --json-report --json-report-file=_bmad-output/specforge/pytest-report.json
```

### 4. Populate Directory Layout

Document test directory structure mirroring `src/` per architecture.

### 5. Present to User

Show frameworks table and primary runner command. Confirm it runs correctly in the project.

**[C] Continue to validation**

HALT — wait for [C].

## SUCCESS METRICS:

✅ Frameworks table populated for levels used
✅ Primary runner command is single executable shell line
✅ Directory layout documented

## NEXT STEP:

After [C], load `./step-05-validate.md`.
