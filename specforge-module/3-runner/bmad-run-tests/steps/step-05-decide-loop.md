# Step 5: Decide Loop

## MANDATORY EXECUTION RULES (READ FIRST):

- 📖 CRITICAL: Read complete step file before acting
- 🚫 5-iteration cap enforced HERE — no bypass
- 🚫 Do NOT auto-invoke other workflows — emit handoff for user
- 🚫 NEVER edit src/, tests, or docs

## YOUR TASK:

Decide: green complete, dev handoff, or loop-cap halt.

## DECISION LOGIC:

Read `{specforge_artifacts}/last-run.json` just written. Let `{{iteration}}` = `iteration` field.

### Path A: Green Build

**IF** `exit_code == 0` **AND** `summary.failed == 0` **AND** `summary.errored == 0`:

→ Proceed to `./step-06-complete.md`

### Path B: Loop Cap (iteration >= 5)

**IF** tests failed (exit_code != 0 OR failed > 0 OR errored > 0) **AND** `{{iteration}} >= 5`:

→ **HALT** with this exact message:

---

**⛔ Loop cap reached (iteration {{iteration}} of 5)**

Tests still failing after 5 patch cycles. The dev workflow will NOT be invoked again.

**Failure summary:**
- Command: `{command from last-run.json}`
- Failed: `{summary.failed}`, Errored: `{summary.errored}`
- Report: `{specforge_artifacts}/last-run.json`

Review failures manually. Options:
1. Fix issues directly and re-run `bmad-run-tests`
2. Invoke `bmad-investigate` for forensic analysis
3. Invoke `bmad-correct-course` if requirements or architecture need change

---

**STOP.** Do not load step-06. Do not invoke dev.

### Path C: Dev Handoff (failed AND iteration < 5)

**IF** tests failed **AND** `{{iteration}} < 5`:

→ Emit this exact handoff message (bmm has no dedicated patch-mode workflow):

---

**🔴 Tests failed at iteration {{iteration}}**

Invoke bmm's dev agent and instruct it to read `{specforge_artifacts}/last-run.json` and patch `src/` only.

**Hard rule for the dev:** never edit tests.

**Handoff context for Amelia (bmad-agent-dev):**
- Read `{specforge_artifacts}/last-run.json` completely
- For each failure, inspect `suspected_source_files` and fix source code only
- Use `fr_id` and `assertion` fields to understand expected behavior
- Do NOT modify test files, test-strategy.md, or last-run.json
- After patches complete, invoke the `bmad-run-tests` workflow again

---

**HALT** — user drives the loop. Wait for user to run dev, then re-invoke `bmad-run-tests`.

## NEXT STEP:

- Green → `./step-06-complete.md`
- Red + iter < 5 → HALT (handoff emitted)
- Red + iter >= 5 → HALT (loop cap)
