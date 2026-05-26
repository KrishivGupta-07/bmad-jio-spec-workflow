---
workflowType: 'run-tests'
---

# Run Tests Workflow

**Goal:** Prepare the test environment once per environment, execute the runner command from test-strategy.md, write structured results to last-run.json, and decide green completion, dev handoff, or loop-cap halt (5-iteration maximum).

**Your Role:** Deterministic test execution orchestrator. Run commands verbatim; parse output; write reports; emit handoffs. Do NOT edit source code, tests, or documentation.

---

## WORKFLOW ARCHITECTURE

Micro-file steps with sequential enforcement. Load only the current step file. Environment setup runs before the first test execution and is skipped on later iterations when `.specforge/env-ready` hash matches test-strategy.md.

---

## EXECUTION

Read fully and follow each step in order:

1. `./steps/step-01-init.md` — load test strategy, extract runner command, prepare iteration counter
2. `./steps/step-01b-ensure-environment.md` — run Environment Setup once per environment (hash-gated by `.specforge/env-ready`)
3. `./steps/step-02-execute.md` — execute runner command
4. `./steps/step-03-parse-failures.md` — parse structured test output
5. `./steps/step-04-write-report.md` — write last-run.json
6. `./steps/step-05-decide-loop.md` — green / handoff / loop-cap halt
7. `./steps/step-06-complete.md` — complete on green build

**Note:** Step-01 must not run setup commands. Step-01b owns environment preparation exclusively.
