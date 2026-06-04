from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import instructions, metrics, projects, runs, ws
from app.config import get_settings
from app.db import init_db
from app.services.workspace import kickoff_template_build


@asynccontextmanager
async def lifespan(_app: FastAPI):
    import asyncio
    from sqlalchemy import select, update
    from app.models.run import Run, RunStatus
    from app.db import async_session
    from app.services.poller import start_polling, active_choreographies

    await init_db()

    # Startup Reconciliation: Find runs stuck in 'running' and mark them 'failure'
    async with async_session() as session:
        await session.execute(
            update(Run)
            .where(Run.status == RunStatus.running)
            .values(status=RunStatus.failure)
        )
        await session.commit()

    kickoff_template_build()
    
    # Start the background poller
    _app.state.poller_task = asyncio.create_task(start_polling())

    yield
    
    try:
        from app.services.langfuse_sink import langfuse_sink
        langfuse_sink.shutdown()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Error shutting down Langfuse sink: {e}")

    # Clean Teardown
    if hasattr(_app.state, "poller_task"):
        _app.state.poller_task.cancel()
        try:
            await _app.state.poller_task
        except asyncio.CancelledError:
            pass
            
    for task in active_choreographies.values():
        task.cancel()
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
    app.include_router(instructions.router, prefix="/api")
    app.include_router(runs.router, prefix="/api")
    app.include_router(metrics.router, prefix="/api")
    app.include_router(ws.router, prefix="/api/ws")
    return app


app = create_app()
