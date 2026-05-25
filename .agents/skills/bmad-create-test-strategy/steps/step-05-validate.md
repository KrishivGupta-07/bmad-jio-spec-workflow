# Step 5: Validate Test Strategy

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: ALWAYS read the complete step file before taking any action
- ✅ Run `../checklist.md` gate criteria — ALL must pass
- 🚫 HALT if any gate fails
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in `{communication_language}`

## EXECUTION PROTOCOLS:

- 🎯 Load and execute every gate criterion in `../checklist.md`
- 💾 Fix failures collaboratively before proceeding
- 📖 Update frontmatter `stepsCompleted: [1, 2, 3, 4, 5]` only after all gates pass
- 🚫 FORBIDDEN to proceed to step-06 if validation fails

## YOUR TASK:

Run the create-test-strategy checklist and gate the document for completion.

## VALIDATION PROCESS:

### 1. Load Checklist

Read `../checklist.md` completely.

### 2. Execute Gate Criteria

For each gate criterion, inspect `{output_file}` and report PASS or FAIL with evidence:

| Criterion | Result | Evidence |
| --- | --- | --- |
| Every FR-ID in matrix | PASS/FAIL | … |
| Coverage targets per module | PASS/FAIL | … |
| Single runner command line | PASS/FAIL | … |
| Risk priority with FR + reasoning | PASS/FAIL | … |
| Test levels assigned | PASS/FAIL | … |
| Frameworks table populated | PASS/FAIL | … |

### 3. Cross-Reference FSD

Load FSD FR-ID list and verify 1:1 coverage in matrix — no missing, no orphan IDs.

### 4. Handle Failures

If ANY gate fails:

- List specific fixes needed
- Remediate with user
- Re-run validation
- **HALT** until all gates pass

**[C] Continue to completion**

HALT — wait for [C] only after ALL gates pass.

## SUCCESS METRICS:

✅ All checklist gate criteria PASS
✅ Full FR-ID traceability confirmed

## NEXT STEP:

After [C], load `./step-06-complete.md`.
