from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import artifacts, metrics, projects, runs, ws
from app.config import get_settings
from app.db import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="specforge-web", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(projects.router, prefix="/api")
    app.include_router(runs.router, prefix="/api")
    app.include_router(artifacts.router, prefix="/api")
    app.include_router(metrics.router, prefix="/api")
    app.include_router(ws.router, prefix="/api/ws")
    return app


app = create_app()
