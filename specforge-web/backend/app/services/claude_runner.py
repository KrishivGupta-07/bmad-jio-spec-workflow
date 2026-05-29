from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from decimal import Decimal
from pathlib import Path
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)

EventCallback = Callable[[dict[str, Any]], Awaitable[None]]


def _extract_text(payload: dict[str, Any]) -> str:
    if "content" in payload and isinstance(payload["content"], str):
        return payload["content"]
    message = payload.get("message") or {}
    if isinstance(message, dict):
        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(str(block.get("text", "")))
            return "\n".join(parts)
    if "result" in payload:
        return str(payload["result"])
    return json.dumps(payload, default=str)[:4000]


def classify_event(event: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    """Return (kind, role, normalized_payload)."""
    kind = str(event.get("type", "unknown"))
    role = "system"
    if kind in ("assistant", "user"):
        role = kind
    elif kind in ("tool_use", "tool_result"):
        role = "tool"
    elif kind == "system":
        role = "system"
    return kind, role, event


# Headless web runs cannot approve sandbox network prompts interactively.
_HEADLESS_CLAUDE_SETTINGS = (
    '{"sandbox":{"network":{"allowedDomains":["api.anthropic.com","*.anthropic.com"]}}}'
)


async def run_skill(
    project_path: Path,
    trigger: str,
    session_uuid: str,
    on_event: EventCallback,
) -> int:
    settings = get_settings()
    proc = await asyncio.create_subprocess_exec(
        settings.claude_cli_path,
        "--print",
        "--output-format",
        "stream-json",
        "--verbose",
        "--permission-mode",
        "auto",
        "--settings",
        _HEADLESS_CLAUDE_SETTINGS,
        "--session-id",
        session_uuid,
        trigger,
        cwd=str(project_path),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    assert proc.stdout is not None
    async for raw in proc.stdout:
        line = raw.decode("utf-8", errors="replace").strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            logger.debug("non-json line: %s", line[:200])
            continue
        await on_event(event)

    if proc.stderr:
        stderr_data = await proc.stderr.read()
        if stderr_data:
            logger.debug("claude stderr: %s", stderr_data.decode("utf-8", errors="replace")[:500])

    return await proc.wait()


def parse_result_usage(event: dict[str, Any]) -> dict[str, Any] | None:
    if event.get("type") != "result":
        return None
    usage = event.get("usage") or {}
    return {
        "model": event.get("model") or usage.get("model") or "claude",
        "prompt_tokens": int(usage.get("input_tokens") or usage.get("prompt_tokens") or 0),
        "completion_tokens": int(usage.get("output_tokens") or usage.get("completion_tokens") or 0),
        "cost_usd": Decimal(str(event.get("total_cost_usd") or usage.get("cost_usd") or 0)),
        "latency_ms": event.get("duration_ms") or event.get("duration_api_ms"),
    }


def extract_session_id(event: dict[str, Any]) -> str | None:
    if event.get("type") != "system":
        return None
    sid = event.get("session_id")
    if sid:
        return str(sid)
    message = event.get("message") or {}
    if isinstance(message, dict) and message.get("session_id"):
        return str(message["session_id"])
    return None
