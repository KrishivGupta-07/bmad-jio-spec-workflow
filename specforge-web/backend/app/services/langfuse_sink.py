from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from langfuse import Langfuse

from app.config import get_settings

logger = logging.getLogger(__name__)


class LangfuseSink:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )
        self._roots: dict[int, Any] = {}
        self._trace_ids: dict[int, str] = {}

    def start_trace(
        self,
        run_id: int,
        skill_name: str,
        session_id: str,
        project_slug: str,
        iteration: int | None = None,
    ) -> str:
        trace_id = f"{session_id}-{run_id}"
        trace = self._client.trace(
            id=trace_id,
            name=skill_name,
            session_id=session_id,
            metadata={
                "project_slug": project_slug,
                "iteration": iteration,
                "run_id": run_id,
                "session_id": session_id,
            },
            tags=[f"project:{project_slug}", f"stage:{skill_name}"],
        )
        self._roots[run_id] = trace
        self._trace_ids[run_id] = trace_id
        return trace_id

    def log_generation(
        self,
        run_id: int,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: Decimal,
        latency_ms: int | None = None,
    ) -> None:
        trace = self._roots.get(run_id)
        if not trace:
            return
        
        # Start a generation within the trace
        trace.generation(
            name="claude-result",
            model=model,
            usage={
                "input": prompt_tokens,
                "output": completion_tokens,
                "total": prompt_tokens + completion_tokens,
                "total_cost": float(cost_usd),
            },
            metadata={"latency_ms": latency_ms},
            end_time=None, # SDK automatically handles timing if wrapped, but here we just log it as completed
        )

    def end_trace(self, run_id: int, status: str) -> None:
        trace = self._roots.pop(run_id, None)
        self._trace_ids.pop(run_id, None)
        if trace:
            trace.update(metadata={"status": status})
            logger.info(f"Trace {run_id} ended with status: {status}")
        self.flush()

    def flush(self) -> None:
        logger.info("Forcing flush of pending Langfuse events...")
        self._client.flush()
        logger.info("Langfuse flush completed.")

    def shutdown(self) -> None:
        logger.info("Shutting down Langfuse client...")
        self._client.shutdown()
        logger.info("Langfuse client shut down.")


langfuse_sink = LangfuseSink()
