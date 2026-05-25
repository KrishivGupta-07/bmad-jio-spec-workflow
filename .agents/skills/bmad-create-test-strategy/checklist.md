# Create Test Strategy — Validation Checklist

Gate criteria for step-05-validate. **ALL must pass** before proceeding to completion.

## Gate Criteria

| # | Criterion | How to Verify |
| --- | --- | --- |
| G1 | Every FR-ID from FSD appears in Coverage Matrix | Extract all FR-IDs from `{planning_artifacts}/fsd.md`; each must have a row in Coverage Matrix |
| G2 | Coverage targets stated per module | Coverage Targets table has at least one row with specific, modest targets |
| G3 | Primary runner command is a single executable shell line | Primary Runner Command section contains exactly one command line runnable from project root |
| G4 | Risk priorities list at least one FR with reasoning | Risk-Based Priorities table has ≥1 row with FR-ID and rationale |
| G5 | Test levels assigned | Each Coverage Matrix row specifies unit, integration, e2e, or combination |
| G6 | Frameworks table populated | Frameworks and Runner table has entries for levels used in the matrix |

## Traceability Check

- FR-IDs in matrix match FSD exactly (no orphans, no invented IDs)
- Test naming convention documented: `test_FR_NNN_*` for runner FR extraction

## Green Build (N/A)

This checklist is for document validation only — not test execution.
