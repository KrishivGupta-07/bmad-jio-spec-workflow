# specforge

A custom BMAD-Method v6.7.1 workflow module powered by a local web orchestration engine (`specforge-web`). 

Specforge extends the base `bmm` workflow by enforcing a strict functional spec artifact (FSD), a dedicated test strategy, and an automated test-execution loop. With the new **specforge-web** interface, you can orchestrate this entire pipeline manually via a sleek local dashboard, or completely automatically using the background Auto-Advance Choreography engine.

---

## 🌟 The Web Interface & Orchestration

Specforge includes a unified, containerized web platform that manages projects, visualizes artifacts, and tracks usage—no API keys required (it runs via the authenticated Claude CLI).

### Quick Start
All services (Langfuse, PostgreSQL, FastAPI Backend, React Frontend) are consolidated into a single Docker Compose stack:
```bash
cd specforge-web
cp .env.example .env
docker compose up -d --build
```
- **Frontend UI:** `http://localhost:5173`
- **Langfuse Traces:** `http://localhost:3000` (Login: `admin@local.dev` / `password`)

### 🗂️ Projects, Instructions & Resume
A **project** is an empty group; you add one or more **instructions** to it (in the UI or via `auto_advance.txt`). Each instruction is a single prompt that runs the full pipeline inside its own isolated directory (`<project>/instructions/<summary-slug>/`) with its own artifacts, `src/`, and `tests/`. The UI shows every instruction grouped under its project and lets you expand a group to inspect each run.

Runs are **resumable and non-breaking**: when an instruction (re)starts, the engine scans its `_bmad-output` folder, skips any stage whose artifact already exists, and continues from the first incomplete stage. Artifacts are discovered recursively, so BMAD's nested/timestamped outputs (e.g. `planning-artifacts/prds/prd-…/prd.md`) always surface.

### 🤖 Auto-Advance Choreography
Instead of manually triggering pipeline stages, you can let the background worker orchestrate the entire BMAD 4-Phase Development Cycle for you. 

The backend continuously polls your active project workspaces. To trigger a run:
1. Create a file named `auto_advance.txt` in your project's workspace directory.
2. Add `run = true` as the first line, followed by your instructions.
```text
run = true
Build a fully responsive React login page with a dark mode toggle.
```
The system will safely consume the file, flip it to `run = false`, create a new instruction directory for the prompt, and orchestrate:
1. **Analysis:** (`bmad-create-prd`)
2. **Planning:** (`bmad-create-epics-and-stories` / FSD generation)
3. **Solutioning:** (`bmad-create-architecture`)
4. **Implementation Iteration:** A closed loop of E2E test generation, test execution, and source patching up to a 5-iteration cap.

Every step in this choreography emits dedicated, distinct spans to Langfuse natively tagged with the genuine BMAD skill IDs.

---

## 🏗️ What the Specforge Module Adds

Specforge sits on top of an existing BMAD installation, reusing native agents wherever possible, while adding three critical workflows:

**1. Functional Spec Document (FSD)**  
Unlike a product-flavored PRD, the FSD translates user stories into testable functional requirements with explicit IDs (FR-001, FR-002) and Given/When/Then acceptance criteria. Tech choices and test cases are strictly forbidden here and pushed downstream.

**2. Test Strategy Workflow**  
Reads the FSD and architecture to produce a coverage matrix where every FR-ID maps to a test level. It captures environment setup commands independently from the test runner command. 

**3. Test-Execution Loop (5-Iteration Cap)**  
A dedicated runner executes tests and outputs structured failures to `last-run.json`. It hands off failures to the dev agent (`bmad-quick-dev`) with explicit instructions to patch `src/` only—never the tests. This loop continues until green or until a hard 5-iteration cap is reached.

---

## 🔄 The End-to-End Pipeline

Whether triggered manually via the UI or automatically via Auto-Advance, the pipeline flows as follows:

```text
  → bmad-create-prd            (bmm)       → prd.md
  → bmad-create-epics-and-stories / fsd    → fsd.md
  → bmad-create-architecture   (bmm)       → architecture.md
  → bmad-create-test-strategy  (specforge) → test-strategy.md
  → bmad-quick-dev             (bmm)       → src/**
  → bmad-qa-generate-e2e-tests (bmm)       → tests/**           
  → bmad-run-tests             (specforge) → last-run.json
        on failure (iter < 5):
          → bmad-quick-dev     (bmm)       → patches src/ only
          → bmad-run-tests     (specforge) → updated last-run.json
        on iter ≥ 5:
          HALT — surface to human
        on green:
          done
```
*FR-IDs trace end-to-end: assigned in the FSD, mapped in architecture, covered in test-strategy, and surfaced in `last-run.json` failures.*

---

## 📂 Module Layout & Editing

The canonical source for the custom skills lives in `specforge-module/` at the repo root. 

```text
specforge-module/                          (authoritative source — edit here)
├── module.yaml
├── 1-fsd/bmad-create-fsd/
├── 2-test-strategy/bmad-create-test-strategy/
└── 3-runner/
    ├── bmad-agent-runner/
    └── bmad-run-tests/
```

**Editing the Module:**
Never edit `_bmad/specforge/` or `.agents/skills/` directly, as the installer overwrites them. If you make changes to `specforge-module/`, recompile the skills so the IDE (and the web orchestration) sees the change:

```bash
npx bmad-method install --directory . --modules bmm \
  --custom-source ./specforge-module --tools cursor --yes --action update
```

## 🚫 Hard Rules & Non-Goals
- **No Test Editing:** The dev agent patches `src/` only when invoked via the runner's handoff. Editing tests to make them pass is a violation.
- **5-Iteration Hard Halt:** The runner refuses to invoke pytest a 6th time if the prior `last-run.json` shows tests still failing.
- **No Local API Keys:** The backend web runner utilizes the Claude CLI OAuth flow; no proxy or raw API keys are required.
- **No Inline Editing:** The Web UI is an orchestration and visualization dashboard, not an inline markdown editor.
