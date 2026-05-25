# specforge

A custom BMAD-Method v6.7.1 module that extends bmm with a stricter spec artifact, a dedicated test strategy artifact, and an automated test-execution loop.

## What this is

specforge sits on top of an existing BMAD installation. It does not replace bmm — it reuses bmm's analyst, pm, architect, sm, dev, and qa agents wherever possible and adds three things bmm does not provide natively.

The canonical source lives in `specforge-module/` at the repo root. The BMAD installer copies it into `_bmad/specforge/` and compiles it to runtime skills under `.agents/skills/`. Edits go to `specforge-module/`, never to `_bmad/specforge/` or `.agents/skills/`.

## What it adds, in plain terms

**An FSD (Functional Spec Document) workflow.** bmm's PRD is product-flavored — user stories, market context, success metrics. The FSD takes that PRD and translates each user story into testable functional requirements with explicit IDs (FR-001, FR-002, …) and Given/When/Then acceptance criteria. The FSD is what the architect and test author actually build against. Tech choices and test cases are forbidden in the FSD by design — those belong downstream.

**A Test Strategy workflow.** bmm has a QA agent but no dedicated strategy artifact. specforge adds one that reads the FSD and the architecture document and produces a strategy with a coverage matrix where every FR-ID maps to at least one test level (unit, integration, e2e). The strategy also captures environment setup commands separately from the runner command, so a clean machine can reproduce the pipeline. The runner command is required to include a structured-output flag — text parsing of test failures was removed deliberately.

**A test-execution loop.** A new `runner` agent (the only new agent specforge defines) executes the test suite, parses structured framework output, writes `_bmad-output/specforge/last-run.json` with failure details, and emits a handoff to bmm's dev agent on failure. The dev patches `src/` only — never tests — and the loop continues until green or until the 5-iteration cap is hit. The cap is a hard stop. The user drives loop transitions; nothing auto-invokes anything.

## How this differs from stock BMAD

| Concern | bmm (stock) | specforge (this module) |
|---|---|---|
| Primary planning artifact | PRD | PRD + FSD (FSD derived from PRD) |
| Requirement traceability | user stories | explicit FR-IDs threaded end-to-end |
| Acceptance criteria | free-form per story | Given/When/Then, one per FR, gated by checklist |
| Test strategy | implicit in QA agent's behavior | first-class document with coverage matrix |
| Test execution | manual or ad-hoc | runner agent with structured failure reports |
| Failure handling | human reads output, talks to dev | runner produces `last-run.json`, hands off to dev with explicit "patch src only, never edit tests" instruction |
| Loop control | none | 5-iteration cap with hard halt |
| Environment setup | assumed | captured separately in test-strategy, run once per environment with hash-gated marker |

specforge does not add: sprint planning, story sharding, epics, or any other Agile machinery. Those live in bmm and you use them or not depending on project size. specforge has been validated against bmm's `bmad-quick-dev` path (no sprint state); it should also work with `bmad-dev-story` but that path has not been exercised.

## The end-to-end pipeline

```
paragraph
  → bmad-create-prd            (bmm)   → _bmad-output/planning-artifacts/prd.md
  → bmad-create-fsd        (specforge) → _bmad-output/planning-artifacts/fsd.md
  → bmad-create-architecture   (bmm)   → _bmad-output/planning-artifacts/architecture.md
  → bmad-create-test-strategy (specforge) → _bmad-output/planning-artifacts/test-strategy.md
  → bmad-quick-dev             (bmm)   → src/**
  → bmad-qa-generate-e2e-tests (bmm)   → tests/**           (test-after)
  → bmad-run-tests         (specforge) → _bmad-output/specforge/last-run.json
        on failure (iter < 5):
          → bmad-quick-dev     (bmm)   → patches src/ only, never tests
          → bmad-run-tests   (specforge) → updated last-run.json
        on iter ≥ 5:
          HALT — surface to human
        on green:
          done
```

FR-IDs trace end to end: assigned in the FSD, mapped to components in the architecture, covered in the test-strategy matrix, embedded in test function names as `test_FR_NNN_<scenario>`, and surfaced in `last-run.json` failures so the dev agent can locate the relevant requirement when patching.

## Module layout

```
specforge-module/                          (authoritative source — edit here)
├── module.yaml
├── config.yaml
├── module-help.csv
├── .claude-plugin/marketplace.json        (lists nested skill paths)
├── 1-fsd/bmad-create-fsd/
│   ├── SKILL.md, customize.toml, template.md, checklist.md
│   └── steps/  (step-01-init … step-06-complete)
├── 2-test-strategy/bmad-create-test-strategy/
│   ├── SKILL.md, customize.toml, template.md, checklist.md
│   └── steps/  (step-01-init … step-06-complete)
└── 3-runner/
    ├── bmad-agent-runner/                 (the only new agent)
    │   ├── SKILL.md, customize.toml
    └── bmad-run-tests/
        ├── SKILL.md, customize.toml, checklist.md
        └── steps/  (step-01-init, step-01b-ensure-environment, step-02-execute, step-03-parse-failures, step-04-write-report, step-05-decide-loop, step-06-complete)
```

After install, the runtime layer at `.agents/skills/` contains four new entries: `bmad-create-fsd`, `bmad-create-test-strategy`, `bmad-agent-runner`, `bmad-run-tests`. These are what the IDE actually reads.

## Why v6.7.1 deviates from older BMAD docs

If you've read older BMAD documentation or expansion-pack examples, the file shapes here will look unfamiliar:

- v6.7.1 uses **SKILL.md + customize.toml** per skill, not the older `.agent.yaml` / `workflow.md` split.
- Nested phase folders need a **`.claude-plugin/marketplace.json`** at the module root listing skill paths — the direct-mode installer scanner only goes one level deep without it.
- The canonical source must live **outside `_bmad/`** because the installer wipes and replaces `_bmad/<module>/` on each install. specforge-module/ is that external source.
- bmm has **no test-patch-mode workflow** as of 6.7.1, so the runner's failure handoff uses `bmad-quick-dev` (or `bmad-dev-story` if sprint state is present) with explicit text instructions, rather than invoking a dedicated patch workflow.

These are not workarounds — they're how v6.7.1 actually works. Older BMAD references describe a different (and now superseded) layout.

## Installing and recompiling

After any edit to `specforge-module/`, recompile so the IDE sees the change:

```bash
npx bmad-method install --directory . --modules bmm \
  --custom-source ./specforge-module --tools cursor --yes --action update
```

This copies the module into `_bmad/specforge/`, compiles it into `.agents/skills/`, and refreshes the manifest. Substitute `--tools cursor` with your IDE if different.

## Verifying the changes

The cheapest way to confirm specforge is installed and current:

```bash
# Four specforge skills should be present
ls .agents/skills/ | grep -E "bmad-(create-fsd|create-test-strategy|agent-runner|run-tests)"

# Total skill count should be 48 (44 bmm/core + 4 specforge)
ls .agents/skills/ | wc -l

# Module entry in the manifest
cat _bmad/_config/manifest.yaml | grep -A2 specforge
```

To inspect what an agent actually receives at runtime:

```bash
head -40 .agents/skills/bmad-create-fsd/SKILL.md
head -40 .agents/skills/bmad-run-tests/SKILL.md
```

To see the FR-ID convention in action after a real run:

```bash
cat _bmad-output/planning-artifacts/fsd.md | grep -E "^\| FR-"
cat _bmad-output/planning-artifacts/test-strategy.md | grep -A50 "Coverage Matrix"
cat _bmad-output/specforge/last-run.json | python -m json.tool | head -40
```

## Invoking the workflows

In your IDE, use natural language matching the skill names:

| Trigger phrase | Skill | When to run |
|---|---|---|
| "Create FSD from my PRD" | `bmad-create-fsd` | After bmm produces a PRD |
| "Create test strategy" | `bmad-create-test-strategy` | After FSD and architecture both exist |
| "Run tests" | `bmad-run-tests` | After src/ and tests/ exist |
| "Talk to Rex" (the runner agent) | `bmad-agent-runner` | When you want the runner persona's menu, e.g. to inspect last-run.json |

On test failure inside iteration cap, the runner emits a handoff message naming the dev skill and the path to `last-run.json`. You invoke that dev skill manually — specforge does not auto-invoke other agents, which matches v6 conventions.

## Hard rules worth knowing

These are encoded across multiple step files and checklists, but worth surfacing here so you know what specforge guarantees and what it refuses:

- The FSD contains no tech-stack choices and no test cases. Both are checklist-enforced halts.
- Open questions in the FSD halt the pipeline until the user resolves them. The architect never sees an FSD with unresolved questions.
- Every FR-ID from the FSD must appear in the test-strategy coverage matrix.
- The runner command must include a structured-output flag (`--json-report`, `--json`, `--reporter=json`, or stack equivalent). Text-based failure parsing is not a fallback — it was removed.
- Environment setup runs once per environment, gated by `.specforge/env-ready` and a sha256 hash of test-strategy.md. Edits to setup commands trigger re-setup on the next run.
- The runner never edits source, tests, docs, or test-strategy. It is read-and-execute only.
- The dev agent patches `src/` only when invoked via the runner's handoff. Editing tests to make them pass is a violation; the handoff message states this explicitly.
- The 5-iteration cap is a hard halt. The runner refuses to invoke pytest a 6th time when the prior `last-run.json` shows `iteration: 5` and tests still fail.
- `last-run.json` has exactly one writer: the runner agent. The dev agent reads it; no other component writes to it.

## Status and validation

The pipeline has been validated end-to-end on at least one project:

> PRD → FSD → architecture → test strategy → code → tests → run → dev handoff (src-only) → green at iteration 2.

The 5-iteration cap has not yet been stress-tested against a deliberately impossible test. Until that's done, treat the cap as load-bearing-but-unverified — if you see specforge approaching iteration 5 on a real project, watch the next invocation to confirm it actually halts.

The pipeline has been exercised against `bmad-quick-dev`. The `bmad-dev-story` path (projects with sprint-status.yaml) is supported by the handoff logic but has not been run end-to-end.

## What's intentionally not here

- No sprint planning, epics, or story files — those live in bmm.
- No automatic loop orchestration — the user invokes each step.
- No retry logic inside a single iteration — one pytest invocation per iteration, no flake handling.
- No test mutation, generation of additional tests, or coverage gap-filling beyond what the qa agent produces. The runner is a pure executor.
- No support for non-structured test output. The runner expects JSON and halts politely if it doesn't get it.

## Editing specforge itself

Source of truth: `specforge-module/`.

Workflow for changes:
1. Edit files under `specforge-module/`.
2. Run the recompile command above.
3. Verify the change appears under `.agents/skills/` with the verification commands.
4. Re-invoke the affected skill from your IDE to test.

Do not edit `_bmad/specforge/` directly — the installer will overwrite it on the next run. Do not edit `.agents/skills/` directly — it's generated.
