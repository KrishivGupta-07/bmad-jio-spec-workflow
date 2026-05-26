from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.run_manager import run_hub

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/runs/{run_id}")
async def run_events_ws(websocket: WebSocket, run_id: int) -> None:
    await websocket.accept()
    queue = run_hub.subscribe(run_id)
    try:
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                await websocket.send_json(event)
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "ping"})
    except WebSocketDisconnect:
        pass
    finally:
        run_hub.unsubscribe(run_id, queue)
