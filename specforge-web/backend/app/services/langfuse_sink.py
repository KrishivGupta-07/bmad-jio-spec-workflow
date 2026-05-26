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
        trace_id = self._client.create_trace_id(seed=session_id)
        root = self._client.start_observation(
            trace_context={"trace_id": trace_id},
            name=skill_name,
            metadata={
                "project_slug": project_slug,
                "iteration": iteration,
                "run_id": run_id,
                "session_id": session_id,
                "tags": [f"project:{project_slug}", f"stage:{skill_name}"],
            },
        )
        self._roots[run_id] = root
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
        root = self._roots.get(run_id)
        if not root:
            return
        gen = root.start_observation(
            as_type="generation",
            name="claude-result",
            model=model,
            usage_details={
                "input": prompt_tokens,
                "output": completion_tokens,
                "total": prompt_tokens + completion_tokens,
            },
            cost_details={"total": float(cost_usd)},
            metadata={"latency_ms": latency_ms},
        )
        gen.end()

    def end_trace(self, run_id: int, status: str) -> None:
        root = self._roots.pop(run_id, None)
        self._trace_ids.pop(run_id, None)
        if root:
            root.update(metadata={"status": status})
            root.end()
        self._client.flush()

    def flush(self) -> None:
        self._client.flush()


langfuse_sink = LangfuseSink()
