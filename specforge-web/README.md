# specforge-web

Local web interface and orchestration backend for the BMAD-Method workflow extended by the **specforge** module. 

`specforge-web` provides a complete local pipeline to manage projects, view artifacts, and trigger Claude Code CLI runs without needing API keys (runs via CLI OAuth). It includes a sleek **Frontend UI**, native **Langfuse** observability, and a powerful **Auto-Advance Choreography** engine.

## ✨ Key Features

- **Integrated Frontend UI:** A sleek, local dashboard to manage project workspaces, view generated artifacts (PRDs, FSDs, architectures), and manually trigger individual pipeline stages.
- **Auto-Advance Agent Choreography:** A background polling system that fully automates the BMAD 4-Phase Development Cycle (Analysis, Planning, Solutioning, Implementation) based on a single instruction file.
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
The backend continuously polls your active projects every 10 minutes (configurable via `POLL_INTERVAL_SECONDS`). It looks for a file named `auto_advance.txt` in your project's workspace directory.

**To trigger an automated run:**
1. Create or edit `auto_advance.txt` in your project's workspace.
2. Set the first line to `run = true`.
3. Add your instructions below it.

```text
run = true
Build a fully responsive React login page with a dark mode toggle.
```

The background worker will safely consume the file (flipping it to `run = false`), and orchestrate the following BMAD phases sequentially:
1. **Analysis:** Generates the PRD (`bmad-create-prd`)
2. **Planning:** Breaks requirements into epics and stories (`bmad-create-epics-and-stories`)
3. **Solutioning:** Generates the technical architecture (`bmad-create-architecture`)
4. **Implementation:** Executes a test-driven iterative loop:
   - Generates E2E Tests (`bmad-qa-generate-e2e-tests`)
   - Runs Tests (`bmad-run-tests`)
   - Auto-patches the source code based on test failures (`bmad-quick-dev`) using `last-run.json` handoffs (capped at 5 iterations).

You can monitor the progress of these phases in real-time in the UI Kanban board or view their distinct spans in the Langfuse traces dashboard!

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
