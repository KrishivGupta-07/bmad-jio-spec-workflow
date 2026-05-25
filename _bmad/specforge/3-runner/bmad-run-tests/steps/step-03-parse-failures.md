# Step 3: Parse Failures

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER edit src/, tests, or docs
- 📖 CRITICAL: Read complete step file before acting
- ✅ Prefer structured JSON framework output
- ✅ Fall back to text parsing ONLY when structured output unavailable
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in `{communication_language}`

## YOUR TASK:

Parse test output into structured failure records for last-run.json.

## PARSING PROTOCOL:

### 1. Locate Structured Output

Check for framework JSON reports written by the runner command:

- pytest: `{specforge_artifacts}/pytest-report.json` or `--json-report-file` path
- jest: `{specforge_artifacts}/jest-report.json` or `--outputFile` path
- vitest: `{specforge_artifacts}/vitest-report.json` or `--outputFile` path

If structured JSON exists, parse it preferentially.

### 2. Build Summary Counts

Compute:

```json
"summary": {
  "total": <int>,
  "passed": <int>,
  "failed": <int>,
  "errored": <int>,
  "skipped": <int>
}
```

### 3. Build Failures Array

For each failed/errored test, create a failure object:

```json
{
  "test_id": "<full test name>",
  "fr_id": "<FR-NNN or null>",
  "file": "<test file path>",
  "line": <integer or null>,
  "assertion": "<failure message>",
  "expected": "<expected or null>",
  "actual": "<actual or null>",
  "stack_excerpt": "<relevant stack lines>",
  "suspected_source_files": ["<src paths inferred from stack>"]
}
```

### 4. Extract FR-ID

From `test_id`, extract FR-ID using pattern `test_FR_NNN_*` or `test_fr_NNN_*` (case-insensitive).

- Match: set `fr_id` to `FR-NNN`
- No match: set `fr_id` to `null`

### 5. Text Parsing Fallback

If no structured JSON available:

- Parse stdout/stderr for failure blocks
- Extract test names, file paths, assertion messages, stack traces
- Apply same FR-ID extraction rules

### 6. Report Parse Summary

Report to user: total/passed/failed/errored/skipped counts, failure count parsed.

Do NOT write last-run.json yet — step-04 handles writing.

## NEXT STEP:

Load `./step-04-write-report.md`.
