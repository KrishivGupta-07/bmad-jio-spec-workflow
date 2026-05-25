# Step 5: Validate FSD

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: ALWAYS read the complete step file before taking any action
- ✅ Run `../checklist.md` gate criteria — ALL must pass
- 🚫 HALT if any open question remains unresolved
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in `{communication_language}`

## EXECUTION PROTOCOLS:

- 🎯 Load and execute every gate criterion in `../checklist.md`
- 💾 Fix failures collaboratively before proceeding
- 📖 Update frontmatter `stepsCompleted: [1, 2, 3, 4, 5]` only after all gates pass
- 🚫 FORBIDDEN to proceed to step-06 if validation fails

## YOUR TASK:

Run the create-fsd checklist and gate the document for completion.

## VALIDATION PROCESS:

### 1. Load Checklist

Read `../checklist.md` completely.

### 2. Execute Gate Criteria

For each gate criterion, inspect `{output_file}` and report PASS or FAIL with evidence:

| Criterion | Result | Evidence |
| --- | --- | --- |
| Every FR has an ID | PASS/FAIL | … |
| Every FR has ≥1 AC (G/W/T) | PASS/FAIL | … |
| No compound scenarios | PASS/FAIL | … |
| No tech stack choices | PASS/FAIL | … |
| No test cases | PASS/FAIL | … |
| Open Questions section exists | PASS/FAIL | … |
| No unresolved open questions | PASS/FAIL | … |

### 3. Handle Failures

If ANY gate fails:

- List specific fixes needed (FR-IDs, section names)
- Remediate with user
- Re-run validation
- **HALT** until all gates pass

### 4. Non-Functional Notes Check

Ensure Non-Functional Notes section contains ONLY items implied by PRD. Remove any architecture or tech leakage.

**[C] Continue to completion**

HALT — wait for [C] only after ALL gates pass.

## SUCCESS METRICS:

✅ All checklist gate criteria PASS
✅ No Open status in Open Questions table

## NEXT STEP:

After [C], load `./step-06-complete.md`.
