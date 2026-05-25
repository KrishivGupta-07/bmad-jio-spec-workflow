# Create FSD — Validation Checklist

Gate criteria for step-05-validate. **ALL must pass** before proceeding to completion.

## Gate Criteria

| # | Criterion | How to Verify |
| --- | --- | --- |
| G1 | Every FR has an ID | Scan Functional Requirements table — every row has `FR-NNN` format, sequential, no gaps |
| G2 | Every FR has ≥1 AC in Given/When/Then form | Each FR-ID subsection in Acceptance Criteria has at least one AC with Given/When/Then bullets |
| G3 | No compound scenarios | Each AC describes exactly one scenario — split compound conditions into separate ACs |
| G4 | No tech stack choices | FSD contains no framework names, language choices, database selections, or architecture decisions |
| G5 | No test cases | FSD contains no test code, test execution steps, or test file references |
| G6 | Open Questions section exists | Open Questions table is present in the document |
| G7 | No unresolved open questions | Every row in Open Questions has Status = **Resolved** or the question was removed with user confirmation |

## Non-Functional Notes Check

- Section contains ONLY items implied by the PRD
- Remove any architecture or technology leakage discovered during validation

## Green Build (N/A)

This checklist is for document validation only — not test execution.
