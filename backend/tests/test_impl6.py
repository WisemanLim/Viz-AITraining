"""impl/6th — legacy fallback, weight matrix, Redis hub, artifact backfill."""
import json

from starlette.testclient import TestClient

from app.models.model_graph import ModelGraph


def test_compare_runs(client, minimal_onnx_bytes) -> None:
    r1 = client.post("/api/v1/runs", json={"name": "a", "params": {"lr": 0.01}})
    r2 = client.post("/api/v1/runs", json={"name": "b", "params": {"lr": 0.001}})
    id1, id2 = r1.json()["id"], r2.json()["id"]

    client.post(
        f"/api/v1/runs/{id1}/metrics/scalars",
        json={"metrics": [{"tag": "loss", "value": 0.9, "step": 0}]},
    )
    client.post(
        f"/api/v1/runs/{id2}/metrics/scalars",
        json={"metrics": [{"tag": "loss", "value": 0.5, "step": 0}]},
    )

    resp = client.get(f"/api/v1/compare?ids={id1},{id2}")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["runs"]) == 2
    assert any(d["key"] == "lr" for d in body["param_diffs"])
    assert body["tags"][0]["tag"] == "loss"


def test_graph_artifact_and_architecture(client, minimal_onnx_bytes) -> None:
    imported = client.post(
        "/api/v1/graphs",
        files={"file": ("m.onnx", minimal_onnx_bytes, "application/octet-stream")},
    )
    assert imported.status_code == 201
    gid = imported.json()["id"]

    artifact = client.get(f"/api/v1/graphs/{gid}/artifact")
    assert artifact.status_code == 200
    assert len(artifact.content) > 0

    arch = client.get(f"/api/v1/graphs/{gid}/architecture")
    assert arch.status_code == 200
    body = arch.json()
    assert len(body["layers"]) >= 2
    assert len(body["edges"]) >= 1
    assert body["formulas"]
    assert body["source"] == "artifact"
    assert body["artifact_missing"] is False
    assert body.get("connections") is not None


def test_legacy_graph_architecture_fallback(client, minimal_onnx_bytes) -> None:
    from app.services.onnx_graph import parse_onnx_bytes

    parsed = parse_onnx_bytes(minimal_onnx_bytes)
    gen = app_get_db_session(client)
    db = next(gen)
    try:
        row = ModelGraph(
            name="legacy.onnx",
            graph_json=json.dumps(parsed),
            opset_version=parsed.get("metadata", {}).get("opset_version"),
            artifact_key=None,
            artifact_backend=None,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        gid = row.id
    finally:
        try:
            next(gen)
        except StopIteration:
            pass

    arch = client.get(f"/api/v1/graphs/{gid}/architecture")
    assert arch.status_code == 200
    body = arch.json()
    assert body["source"] == "graph_json"
    assert body["artifact_missing"] is True
    assert len(body["layers"]) >= 2
    assert len(body["connections"]) >= 1
    matrix = body["connections"][0]["matrix"]
    assert len(matrix) >= 1
    assert len(matrix[0]) >= 1


def app_get_db_session(client: TestClient):
    from app.db.session import get_db

    override = client.app.dependency_overrides.get(get_db)
    if override is None:
        raise RuntimeError("get_db override missing")
    return override()


def test_artifact_backfill(client, minimal_onnx_bytes) -> None:
    from app.services.onnx_graph import parse_onnx_bytes

    parsed = parse_onnx_bytes(minimal_onnx_bytes)
    gen = app_get_db_session(client)
    db = next(gen)
    try:
        row = ModelGraph(
            name="legacy.onnx",
            graph_json=json.dumps(parsed),
            artifact_key=None,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        gid = row.id
    finally:
        try:
            next(gen)
        except StopIteration:
            pass

    assert client.get(f"/api/v1/graphs/{gid}/artifact").status_code == 404

    backfill = client.post(
        f"/api/v1/graphs/{gid}/artifact",
        files={"file": ("m.onnx", minimal_onnx_bytes, "application/octet-stream")},
    )
    assert backfill.status_code == 200
    assert backfill.json()["id"] == gid

    artifact = client.get(f"/api/v1/graphs/{gid}/artifact")
    assert artifact.status_code == 200

    arch = client.get(f"/api/v1/graphs/{gid}/architecture")
    assert arch.status_code == 200
    assert arch.json()["source"] == "artifact"
    assert arch.json()["artifact_missing"] is False


def test_metrics_websocket(client) -> None:
    run = client.post("/api/v1/runs", json={"name": "ws-run"})
    run_id = run.json()["id"]

    with client.websocket_connect(f"/api/v1/ws/runs/{run_id}/metrics") as ws:
        hello = ws.receive_json()
        assert hello["type"] == "connected"

        client.post(
            f"/api/v1/runs/{run_id}/metrics/scalars",
            json={"metrics": [{"tag": "loss", "value": 0.3, "step": 1}]},
        )
        msg = ws.receive_json()
        assert msg["type"] == "scalars"
        assert msg["metrics"][0]["tag"] == "loss"


def test_local_artifact_storage(minimal_onnx_bytes, tmp_path) -> None:
    from app.services import artifact_storage as mod

    storage = mod.LocalArtifactStorage(tmp_path)
    key = storage.put("test/x.onnx", minimal_onnx_bytes, "application/octet-stream")
    assert storage.backend_name() == "local"
    assert storage.get(key) == minimal_onnx_bytes


def test_full_weight_matrix_in_architecture(client, minimal_onnx_bytes) -> None:
    imported = client.post(
        "/api/v1/graphs",
        files={"file": ("m.onnx", minimal_onnx_bytes, "application/octet-stream")},
    )
    gid = imported.json()["id"]
    arch = client.get(f"/api/v1/graphs/{gid}/architecture").json()
    for conn in arch["connections"]:
        rows, cols = conn["shape"]
        assert len(conn["matrix"]) == rows
        assert all(len(row) == cols for row in conn["matrix"])


def test_redis_hub_publish(monkeypatch) -> None:
    import asyncio

    from app.services.metrics_hub import MetricsHub

    published: list[str] = []

    class FakeRedis:
        async def ping(self) -> bool:
            return True

        async def publish(self, channel: str, message: str) -> int:
            published.append(message)
            return 1

        async def aclose(self) -> None:
            pass

        def pubsub(self):
            return FakePubSub()

    class FakePubSub:
        async def subscribe(self, channel: str) -> None:
            pass

        async def listen(self):
            if False:
                yield {}

        async def unsubscribe(self, channel: str) -> None:
            pass

        async def aclose(self) -> None:
            pass

    monkeypatch.setattr("app.core.config.settings.redis_url", "redis://localhost:6379/0")

    hub = MetricsHub()
    hub._redis = FakeRedis()  # noqa: SLF001

    async def run() -> None:
        await hub.broadcast("run-1", {"type": "scalars", "metrics": []})

    asyncio.run(run())
    assert len(published) == 1
    assert "run-1" in published[0]

    asyncio.run(hub.stop())
