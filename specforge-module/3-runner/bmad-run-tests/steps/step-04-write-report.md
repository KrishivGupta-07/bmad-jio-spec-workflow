# Step 4: Write Report

## MANDATORY EXECUTION RULES (READ FIRST):

- 📖 CRITICAL: Read complete step file before acting
- ✅ ONLY this step writes `{specforge_artifacts}/last-run.json`
- 🚫 NEVER edit src/, tests, or docs

## YOUR TASK:

Write `{specforge_artifacts}/last-run.json` per schema.

## WRITE PROTOCOL:

### 1. Compose JSON Document

```json
{
  "timestamp": "<ISO-8601 UTC>",
  "command": "<exact command executed>",
  "exit_code": <integer>,
  "summary": {
    "total": <int>,
    "passed": <int>,
    "failed": <int>,
    "errored": <int>,
    "skipped": <int>
  },
  "failures": [
    {
      "test_id": "<full test name>",
      "fr_id": "<FR-NNN or null>",
      "file": "<test file path>",
      "line": <integer or null>,
      "assertion": "<failure message>",
      "expected": "<expected or null>",
      "actual": "<actual or null>",
      "stack_excerpt": "<relevant stack lines>",
      "suspected_source_files": ["<src paths>"]
    }
  ],
  "iteration": <next_iteration from step-01>
}
```

### 2. Write File

Write to `{specforge_artifacts}/last-run.json` (overwrite prior run).

### 3. Confirm

Report file path and summary counts to user.

## NEXT STEP:

Load `./step-05-decide-loop.md`.
