# specforge-web

Local web interface and orchestration backend for the BMAD-Method workflow extended by the **specforge** module. 

`specforge-web` provides a complete local pipeline to manage projects, view artifacts, and trigger Claude Code CLI runs without needing API keys (runs via CLI OAuth). It includes a sleek **Frontend UI**, native **Langfuse** observability, and a powerful **Auto-Advance Choreography** engine.

## ✨ Key Features

- **Projects as groups of instructions:** A project is an empty group (no prompt needed to create). You then add one or more **instructions** to it. Each instruction is a single prompt that runs the full BMAD pipeline in its own **isolated directory** (`<project>/instructions/<summary-slug>/`) with its own artifacts, `src/`, and `tests/`. The UI groups all instructions under their project in an expandable (shadcn accordion) view.
- **Integrated Frontend UI:** A sleek, local dashboard to manage project groups, add instructions, view generated artifacts (PRDs, FSDs, architectures), watch live runs, and trigger/resume pipeline stages.
- **Resumable & non-breaking:** When an instruction (re)starts — manually, on server restart, or via auto-advance — the engine cross-references the output folder against the workflow and **skips stages whose artifacts already exist**, continuing from the first incomplete stage instead of breaking.
- **Robust artifact discovery:** Artifacts are discovered by scanning `_bmad-output` recursively (BMAD writes to nested, timestamped folders such as `planning-artifacts/prds/prd-…/prd.md`), so PRDs/FSDs/architecture/test-strategy/last-run always surface in the UI.
- **Auto-Advance Agent Choreography:** A background polling system that fully automates the BMAD 4-Phase Development Cycle (Analysis, Planning, Solutioning, Implementation). Each time `auto_advance.txt` is armed, its text becomes a **new instruction** with its own directory.
- **Native Langfuse Observability:** Deep integration with Langfuse v2. All runs emit detailed traces mapped directly to genuine BMAD skills (e.g., `bmad-create-prd`), capturing tokens, latencies, and dollar costs automatically.
- **Unified Docker Deployment:** A single `docker compose` stack effortlessly spins up PostgreSQL, the Langfuse Dashboard, the FastAPI Backend, and the React Frontend.
- **MCP Server:** Exposes Model Context Protocol (MCP) over SSE for external tooling integration.

---

## 🚀 Quick Start (Unified Stack)

All services are containerized and pre-configured to communicate out-of-the-box.

### 1. Configure
Copy the default environment configuration:
```bash
cp .env.example .env
```
*(Optional: verify `SPECFORGE_MODULE_PATH` points to your `specforge-module` directory).*

### 2. Start the Stack
Spin up the entire production-ready stack in the background:
```bash
docker compose up -d --build
```

### 3. Access the Services
- **Frontend UI**: `http://localhost:5173` (Manage projects and pipeline stages)
- **Langfuse Dashboard**: `http://localhost:3000` (Pre-seeded login: `admin@local.dev` / `password`)
- **FastAPI Backend**: `http://localhost:8000`
- **MCP Server (SSE)**: `http://localhost:8765/sse`

---

## 🤖 Auto-Advance Polling & Choreography

Instead of manually clicking through pipeline stages in the UI, `specforge-web` includes a powerful background poller that can automatically run the full BMAD 4-Phase Development cycle on your behalf.

### How it works:
The backend continuously polls every 10 minutes (configurable via `POLL_INTERVAL_SECONDS`). On each cycle it does two things:

1. **Auto-discovers projects.** It scans the immediate subfolders of the scan root (defaults to `WORKSPACE_ROOT`, override with `SCAN_ROOT`). Any folder that contains an `auto_advance.txt` is automatically registered as a project named after the folder. If the folder is missing BMAD scaffolding (`.agents/skills` and `_bmad`), it is seeded from the shared BMAD template in place — your existing source files are left untouched.
2. **Checks each project** for a file named `auto_advance.txt` and triggers a run when it is armed.

This means you do not have to create a project through the UI first. Just drop a folder with an `auto_advance.txt` into the scan root, and it shows up in the UI on the next poll (reload the page to see it).

**To trigger an automated run:**
1. Create or edit `auto_advance.txt` in the folder.
2. Set the first line to `run = true`.
3. Add your instructions below it.

```text
run = true
Build a fully responsive React login page with a dark mode toggle.
```

The background worker will safely consume the file (flipping it to `run = false`), create a **new instruction** (a directory named after a summary of the prompt, e.g. `instructions/build-fully-responsive-react-login/`), seed it with BMAD scaffolding, write the prompt as that instruction's product brief, and then run **exactly the same pipeline stages as the web UI**, in order:
1. **Create PRD** (`bmad-create-prd`)
2. **Create FSD from my PRD** (`bmad-create-fsd`)
3. **Create architecture** (`bmad-create-architecture`)
4. **Create test strategy** (`bmad-create-test-strategy`)
5. **Implement / quick-dev** (`bmad-quick-dev`)
6. **Generate e2e tests** (`bmad-qa-generate-e2e-tests`)
7. **Run tests** (`bmad-run-tests`)

After the first `Run tests`, it enters a **test-driven fix loop**: it reads `last-run.json` and, while tests are failing, auto-patches the source (`bmad-quick-dev`, `src/` only — never tests) and re-runs the suite, capped at 5 iterations. If any stage before `Run tests` fails, the choreography aborts.

You can monitor the progress of these phases in real-time in the UI Kanban board or view their distinct spans in the Langfuse traces dashboard!

> **Note on polling frequency:** the poller runs once immediately on backend startup, then every `POLL_INTERVAL_SECONDS` (default `600` = 10 min). The `auto_advance.txt` first line is flipped to `run = false` as soon as a run is *started* (not when it finishes), so re-arm it with `run = true` to trigger another pass. For faster local iteration, set a lower `POLL_INTERVAL_SECONDS` (e.g. `10`) in `backend/.env`.

---

## 🪪 Per-Run Session IDs & Conversation View

Every run (whether started manually or via Auto-Advance) is assigned a Claude CLI **session ID** (`claude_session_id`), which is used to keep the agent conversation continuous for that run.

- **Session ID is shown in the UI.** Open any run from the dashboard to see its session ID under the run header, so you can correlate a run with its underlying Claude CLI session and Langfuse trace.
- **Prompt is shown separately.** The trigger phrase that drives the run is displayed as a labeled **Prompt** block in the run header rather than appearing as a chat bubble.
- **Cleaner message stream.** The conversation view now filters out blank messages and the prompt echo, and de-duplicates messages that arrive both over the live WebSocket and from the persisted history. This removes the empty/duplicate bubbles (and the confusing `user` bubble that was just the prompt) that previously appeared.

---

## 📋 Pipeline Stages

Whether triggered manually via the UI or orchestrated via Auto-Advance, all runs map to genuine, compiled BMAD skills:

| Stage | Skill | Trigger Description |
|-------|-------|---------|
| PRD | `bmad-create-prd` | Create PRD |
| FSD / Planning | `bmad-create-epics-and-stories` | Break requirements into epics and user stories |
| Architecture | `bmad-create-architecture` | Create technical architecture |
| Test Strategy | `bmad-create-test-strategy` | Create test strategy |
| Implement | `bmad-quick-dev` | Patch `src/` iteratively |
| E2E tests | `bmad-qa-generate-e2e-tests` | Generate e2e tests |
| Run tests | `bmad-run-tests` | Run tests & generate `last-run.json` |

## ⚙️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SPECFORGE_MODULE_PATH` | `../specforge-module` | Path to specforge-module source |
| `WORKSPACE_ROOT` | `../workspace` | Project workspace directory |
| `SCAN_ROOT` | _(unset → `WORKSPACE_ROOT`)_ | Directory whose immediate subfolders with an `auto_advance.txt` are auto-discovered and registered as projects. Must be mounted into the backend container when using Docker. |
| `CLAUDE_CLI_PATH` | `claude` | Claude CLI binary |
| `LANGFUSE_PUBLIC_KEY` | `pk-lf-local-dev` | Langfuse public key |
| `LANGFUSE_SECRET_KEY` | `sk-lf-local-dev` | Langfuse secret key |
| `LANGFUSE_HOST` | `http://localhost:3000` | Langfuse host |
| `POLL_INTERVAL_SECONDS` | `600` | Auto-Advance polling frequency |

## 🛠 MCP Tools

The backend exposes these endpoints to MCP clients:
- `bmad.list_projects`
- `bmad.create_project`
- `bmad.start_stage`
- `bmad.get_run`
- `bmad.read_artifact`
- `bmad.get_last_run`
- `bmad.list_failures`

## 🚫 Non-Goals
- No API keys or LiteLLM proxy required
- No authentication (local-only environment)
- No inline PRD/FSD editing directly in the UI
