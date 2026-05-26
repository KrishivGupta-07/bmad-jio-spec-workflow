# Run Tests — Validation Checklist

## Green Build Gate (step-06-complete only)

Gate criteria for green path completion. **ALL must pass** when routed to step-06.

| # | Criterion | How to Verify |
| --- | --- | --- |
| G1 | exit_code == 0 | `{specforge_artifacts}/last-run.json` exit_code field is 0 |
| G2 | No failures | summary.failed == 0 |
| G3 | No errors | summary.errored == 0 |
| G4 | Report written | last-run.json exists with valid schema |
| G5 | Command recorded | last-run.json command field matches executed primary runner command |

## Loop Cap Gate (step-05-decide-loop)

| # | Criterion | Action |
| --- | --- | --- |
| L1 | iteration >= 5 AND failures present | HALT — do NOT invoke dev, do NOT load step-06 |
| L2 | iteration < 5 AND failures present | Emit dev handoff, HALT — user drives loop |
| L3 | Green build | Proceed to step-06-complete |

## Schema Validation

last-run.json must contain:

- `timestamp` (ISO-8601)
- `command` (string)
- `exit_code` (integer)
- `summary` (object with total, passed, failed, errored, skipped)
- `failures` (array)
- `iteration` (integer)

Each failure object should include: test_id, fr_id, file, line, assertion, expected, actual, stack_excerpt, suspected_source_files.
