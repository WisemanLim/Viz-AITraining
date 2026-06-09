"""WebSocket live metric stream."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.metrics_hub import metrics_hub

router = APIRouter(tags=["metrics"])


@router.websocket("/ws/runs/{run_id}/metrics")
async def metrics_stream(run_id: str, ws: WebSocket) -> None:
    await metrics_hub.connect(run_id, ws)
    try:
        await ws.send_json({"type": "connected", "run_id": run_id})
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await metrics_hub.disconnect(run_id, ws)
