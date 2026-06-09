"""WebSocket broadcast hub — local and Redis pub/sub fan-out."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from fastapi import WebSocket

from app.core.config import settings

logger = logging.getLogger(__name__)

METRICS_CHANNEL = "viz:metrics:live"


class LocalMetricsHub:
    def __init__(self) -> None:
        self._rooms: dict[str, set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, run_id: str, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._rooms.setdefault(run_id, set()).add(ws)

    async def disconnect(self, run_id: str, ws: WebSocket) -> None:
        async with self._lock:
            room = self._rooms.get(run_id)
            if room and ws in room:
                room.discard(ws)
            if room is not None and len(room) == 0:
                del self._rooms[run_id]

    async def fanout(self, run_id: str, payload: dict[str, Any]) -> None:
        async with self._lock:
            sockets = list(self._rooms.get(run_id, set()))
        if not sockets:
            return
        message = json.dumps(payload)
        dead: list[WebSocket] = []
        for ws in sockets:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            await self.disconnect(run_id, ws)


class MetricsHub:
    """Publishes to Redis when configured; always fans out on this process."""

    def __init__(self) -> None:
        self._local = LocalMetricsHub()
        self._redis = None
        self._listener_task: asyncio.Task[None] | None = None

    @property
    def uses_redis(self) -> bool:
        return bool(settings.redis_url)

    async def start(self) -> None:
        if not settings.redis_url:
            return
        try:
            import redis.asyncio as aioredis

            self._redis = aioredis.from_url(settings.redis_url, decode_responses=True)
            await self._redis.ping()
            self._listener_task = asyncio.create_task(self._listen())
            logger.info("MetricsHub Redis pub/sub enabled")
        except Exception as exc:
            logger.warning("Redis unavailable, using in-process hub only: %s", exc)
            self._redis = None

    async def stop(self) -> None:
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
        if self._redis:
            await self._redis.aclose()
            self._redis = None

    async def _listen(self) -> None:
        if self._redis is None:
            return
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(METRICS_CHANNEL)
        try:
            async for message in pubsub.listen():
                if message.get("type") != "message":
                    continue
                data = message.get("data")
                if not isinstance(data, str):
                    continue
                try:
                    envelope = json.loads(data)
                    run_id = envelope["run_id"]
                    payload = envelope["payload"]
                except (json.JSONDecodeError, KeyError, TypeError):
                    continue
                await self._local.fanout(run_id, payload)
        finally:
            await pubsub.unsubscribe(METRICS_CHANNEL)
            await pubsub.aclose()

    async def connect(self, run_id: str, ws: WebSocket) -> None:
        await self._local.connect(run_id, ws)

    async def disconnect(self, run_id: str, ws: WebSocket) -> None:
        await self._local.disconnect(run_id, ws)

    async def broadcast(self, run_id: str, payload: dict[str, Any]) -> None:
        if self._redis is not None:
            envelope = json.dumps({"run_id": run_id, "payload": payload})
            await self._redis.publish(METRICS_CHANNEL, envelope)
        else:
            await self._local.fanout(run_id, payload)


metrics_hub = MetricsHub()
