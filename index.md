# specforge

> TODO: Commit this file as `docs/index.md` to the ROOT of the specforge repo
> (so the path is `docs/index.md`, matching `mkdocs.yml`'s `nav`).

**specforge** is a BMAD-Method spec workflow platform. It wraps
[BMAD-Method](https://github.com/bmad-code-org/BMAD-METHOD) workflows behind a
web app.

## Architecture

- **specforge-web** — FastAPI + React backend that drives the workflows.
- **Langfuse** — observability for LLM calls.
- **Docker Compose** — local orchestration of the services.

## Running locally

```bash
docker compose up -d
```

| Service               | Port |
| --------------------- | ---- |
| Frontend              | 5174 |
| Backend (FastAPI)     | 8000 |
| Langfuse              | 3000 |
| Langfuse Postgres     | 5433 |

## Triggering a pipeline run

Create/overwrite `auto_advance.txt` at the repo root with:

```text
run = true
<your prompt here>
```

The Backstage "Run specforge pipeline" template automates this via a pull request.
