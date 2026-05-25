# Step 5: Validate Test Strategy

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: ALWAYS read the complete step file before taking any action
- ✅ Run `../checklist.md` gate criteria — ALL must pass
- 🚫 HALT on first failure with message naming the exact field that failed
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in `{communication_language}`

## EXECUTION PROTOCOLS:

- 🎯 Load and execute every gate criterion in `../checklist.md` in order (G1 → G9)
- 💾 Fix failures collaboratively before proceeding
- 📖 Update frontmatter `stepsCompleted: [1, 2, 3, 4, 5]` only after all gates pass
- 🚫 FORBIDDEN to proceed to step-06 if validation fails

## YOUR TASK:

Run the create-test-strategy checklist and gate the document for completion.

## VALIDATION PROCESS:

### 1. Load Checklist

Read `../checklist.md` completely.

### 2. Execute Gate Criteria

For each gate criterion G1–G9, inspect `{output_file}` and report PASS or FAIL with evidence.

On **FAIL**, halt immediately and emit a message that names the exact field:

| Gate | Field name on failure |
| --- | --- |
| G1 | `Coverage Matrix` — missing FR-ID(s): list each |
| G2 | `Coverage Targets` — no row with specific modest target |
| G3 | `Environment Setup` — section missing or empty |
| G4 | `Runner Command` — not exactly one executable line |
| G5 | `Runner Command` — missing structured-output flag (`--json-report`, `--json`, `--reporter=json`, `-json`, or equivalent) |
| G6 | `Runner Command` — structured output path does not begin with `.specforge/` |
| G7 | `Risk-Based Priorities` — no FR-ID with rationale |
| G8 | `Coverage Matrix` — row(s) missing test level |
| G9 | `Frameworks and Runner` — table empty for levels used in matrix |

**HALT message format** (use verbatim field name from table):

```
VALIDATION HALT — {Field name}: {specific reason}
```

Do not use a generic "checklist failure" message. Name the field and the concrete defect.

Example failures:

```
VALIDATION HALT — Environment Setup: section missing or fenced block has no command lines
```

```
VALIDATION HALT — Runner Command: missing structured-output flag (--json-report, --json, --reporter=json, -json, or equivalent)
```

```
VALIDATION HALT — Runner Command: structured output path does not begin with .specforge/
```

### 3. Cross-Reference FSD

After G1–G9 all pass, load FSD FR-ID list and verify 1:1 coverage in matrix — no missing, no orphan IDs.

### 4. Handle Failures

If ANY gate fails:

- Emit the HALT message naming the exact field (see §2)
- List specific fixes needed
- Remediate with user
- Re-run validation from G1
- **HALT** until all gates pass

**[C] Continue to completion**

HALT — wait for [C] only after ALL gates pass.

## SUCCESS METRICS:

✅ All checklist gate criteria G1–G9 PASS
✅ Full FR-ID traceability confirmed

## NEXT STEP:

After [C], load `./step-06-complete.md`.
