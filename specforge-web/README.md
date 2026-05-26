# specforge-web

Local web interface for the BMAD-Method v6.7.1 workflow extended by the **specforge** module. Runs pipeline stages via the `claude` CLI (OAuth/subscription — no API keys), tracks usage in Langfuse, and exposes an MCP server.

## Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend and `npx bmad-method install`)
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) authenticated via `claude login`
- Docker (for Langfuse)
- `SPECFORGE_MODULE_PATH` pointing at a real `specforge-module/` directory

## Quick start

### 1. Langfuse

```bash
docker compose -f docker/compose.yaml up -d
```

Langfuse UI: http://localhost:3000 (seeded keys `pk-lf-local-dev` / `sk-lf-local-dev`)

### 2. Backend

```bash
cd backend
cp .env.example .env
# Edit SPECFORGE_MODULE_PATH to your specforge-module directory
pip install -e .
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

UI: http://localhost:5173

### 4. MCP server

```bash
cd backend
python -m app.mcp.server              # stdio
python -m app.mcp.server --sse --port 8765
```

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
