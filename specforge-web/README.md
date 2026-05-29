# specforge-web

Local web interface for the BMAD-Method v6.7.1 workflow extended by the **specforge** module. Runs pipeline stages via the `claude` CLI (OAuth/subscription — no API keys), tracks usage in Langfuse, and exposes an MCP server.

## Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend and `npx bmad-method install`)
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) authenticated via `claude login`
- Docker (for Langfuse)
- `SPECFORGE_MODULE_PATH` pointing at a real `specforge-module/` directory

## Unified Docker Deployment (Single-Command Stack)

All services (Langfuse, PostgreSQL, backend, and frontend) are consolidated into a single, unified Docker Compose configuration.

### 1. Configure Secrets and Paths

First, copy the default environment configuration to `.env` in the `specforge-web` directory:

```bash
cp .env.example .env
```

If necessary, edit the `SPECFORGE_MODULE_PATH` in `.env` to point to your `specforge-module` directory on the host (defaults to `../specforge-module`).

### 2. Start the Stack

To spin up the entire production-ready stack in the background:

```bash
docker compose up -d --build
```

*   **Frontend UI**: `http://localhost:5173` (Served via Nginx proxying `/api` and `/api/ws` automatically to backend)
*   **Langfuse UI**: `http://localhost:3000` (Pre-seeded with local credentials: `admin@local.dev` / `password`)
*   **FastAPI Backend**: `http://localhost:8000`

### 3. Local Development Mode (HMR & Hot-Reloading)

If you are developing or modifying the web interface code and want HMR for Vite and live-reload for FastAPI:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

This mounts the local directories (`./backend` and `./frontend`) inside the containers, runs the Vite dev server inside the container, and proxies HMR and WebSockets seamlessly.

### 4. Running MCP Server inside Docker

The backend container automatically exposes the MCP server on port `8765` over SSE. You can register it in Claude Code or other tools using:

*   **SSE URL**: `http://localhost:8765/sse`

---

## Verifying Langfuse Trace Ingestion

To confirm that trace ingestion is functioning perfectly:

1. Open the **Langfuse UI** at `http://localhost:3000`, log in with `admin@local.dev` / `password`, and verify the `specforge-web` project is preloaded.
2. In the **specforge-web UI** (`http://localhost:5173`), create a new project or select an existing one.
3. Click any **Pipeline Stage** button (such as "Create PRD" or "Create FSD") to kick off a Claude Code CLI run.
4. Open the **FastAPI Backend Logs** (`docker compose logs backend`) to see the debug flush logging:
   ```text
   Forcing flush of pending Langfuse events...
   Successfully flushed OTEL tracer provider
   Langfuse flush completed.
   ```
5. Return to the **Langfuse UI** and check the **Traces** dashboard. You should see a trace named after the stage skill (e.g. `bmad-create-prd`), containing:
   * **Tags**: `project:<slug>` and `stage:<skill_name>`
   * **Metadata**: Project slug, run ID, iteration, session UUID
   * **Generations**: A nested observation named `claude-result` with exact model name, input/output token counts, latency in milliseconds, and calculated dollar cost.


## Architecture

- **One button per pipeline stage** — no auto-chaining unless the user enables "Auto-advance" (off by default).
- **5-iteration runner cap** enforced in UI and runner skill.
- **Runner writes only** `_bmad-output/specforge/last-run.json`; dev handoff patches `src/` only.
- **Langfuse**: one trace per stage run, tagged `project:<slug>` and `stage:<skill_name>`.

## Pipeline stages

| Stage | Skill | Trigger |
|-------|-------|---------|
| PRD | bmad-create-prd | Create PRD |
| FSD | bmad-create-fsd | Create FSD from my PRD |
| Architecture | bmad-create-architecture | Create architecture |
| Test strategy | bmad-create-test-strategy | Create test strategy |
| Implement | bmad-quick-dev | Implement (quick-dev) |
| E2E tests | bmad-qa-generate-e2e-tests | Generate e2e tests |
| Run tests | bmad-run-tests | Run tests |

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SPECFORGE_MODULE_PATH` | `../specforge-module` | Path to specforge-module source |
| `WORKSPACE_ROOT` | `../workspace` | Project workspace directory |
| `CLAUDE_CLI_PATH` | `claude` | Claude CLI binary |
| `LANGFUSE_PUBLIC_KEY` | `pk-lf-local-dev` | Langfuse public key |
| `LANGFUSE_SECRET_KEY` | `sk-lf-local-dev` | Langfuse secret key |
| `LANGFUSE_HOST` | `http://localhost:3000` | Langfuse host |

## MCP tools

- `bmad.list_projects`
- `bmad.create_project`
- `bmad.start_stage`
- `bmad.get_run`
- `bmad.read_artifact`
- `bmad.get_last_run`
- `bmad.list_failures`

## Non-goals

- No API keys or LiteLLM proxy
- No authentication (local-only)
- No inline PRD/FSD editing
- No automatic stage orchestration
