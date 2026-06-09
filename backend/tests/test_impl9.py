"""Phase 3+ — 3D view, internal state, XAI tests."""


def test_internal_metrics_ingest(client) -> None:
    run = client.post("/api/v1/runs", json={"name": "internal-run"})
    run_id = run.json()["id"]

    payload = {
        "metrics": [
            {
                "kind": "activation_map",
                "layer": "conv1",
                "step": 0,
                "title": "Conv1 activations",
                "data": {"width": 2, "height": 2, "values": [[0.1, 0.2], [0.3, 0.4]]},
            },
            {
                "kind": "gradient_flow",
                "step": 1,
                "data": {
                    "timesteps": [0, 1],
                    "layers": ["h0", "h1"],
                    "magnitudes": [[0.5, 0.2], [0.3, 0.1]],
                },
            },
            {
                "kind": "embedding",
                "data": {
                    "method": "tsne",
                    "dim": 2,
                    "points": [{"x": 0.1, "y": 0.2, "label": "a"}],
                },
            },
            {
                "kind": "hidden_state",
                "data": {
                    "timesteps": [0, 1, 2],
                    "states": [[0.1, 0.2], [0.3, 0.1], [0.2, 0.4]],
                },
            },
        ]
    }
    resp = client.post(f"/api/v1/runs/{run_id}/metrics/internal", json=payload)
    assert resp.status_code == 201
    assert resp.json()["total"] == 4

    listed = client.get(f"/api/v1/runs/{run_id}/metrics/internal?kind=embedding")
    assert listed.status_code == 200
    assert listed.json()["total"] == 1


def test_xai_attributions_ingest(client) -> None:
    run = client.post("/api/v1/runs", json={"name": "xai-run"})
    run_id = run.json()["id"]

    payload = {
        "attributions": [
            {
                "method": "shap",
                "scope": "local",
                "data": {
                    "features": ["age", "score"],
                    "values": [0.2, -0.1],
                    "prediction": 0.8,
                },
            },
            {
                "method": "lime",
                "scope": "temporal",
                "step": 100,
                "data": {
                    "steps": [0, 100],
                    "features": ["f1"],
                    "values_over_time": [[0.1], [0.25]],
                },
            },
        ]
    }
    resp = client.post(f"/api/v1/runs/{run_id}/metrics/xai", json=payload)
    assert resp.status_code == 201
    assert resp.json()["total"] == 2

    shap = client.get(
        f"/api/v1/runs/{run_id}/metrics/xai?method=shap&scope=local"
    )
    assert shap.status_code == 200
    assert shap.json()["total"] == 1


def test_architecture_3d_layout(client, minimal_onnx_bytes) -> None:
    imported = client.post(
        "/api/v1/graphs",
        files={"file": ("m.onnx", minimal_onnx_bytes, "application/octet-stream")},
    )
    gid = imported.json()["id"]

    resp = client.get(f"/api/v1/graphs/{gid}/architecture/3d")
    assert resp.status_code == 200
    body = resp.json()
    assert body["graph_id"] == gid
    assert len(body["layers"]) >= 2
    assert len(body["nodes"]) >= 2
    assert "bounds" in body


def test_architecture_3d_service() -> None:
    from app.services.architecture_3d import architecture_to_3d

    arch = {
        "layers": [
            {
                "id": "l0",
                "name": "Input",
                "kind": "input",
                "size": 2,
                "nodes": [
                    {"id": "n0", "index": 0, "activation": 0.5, "hue": "input"},
                    {"id": "n1", "index": 1, "activation": 0.8, "hue": "input"},
                ],
            },
            {
                "id": "l1",
                "name": "Out",
                "kind": "output",
                "size": 1,
                "nodes": [{"id": "n2", "index": 0, "activation": 0.6, "hue": "output"}],
            },
        ],
        "edges": [{"id": "e0", "source": "n0", "target": "n2", "weight": 0.5}],
    }
    layout = architecture_to_3d(arch)
    assert len(layout["nodes"]) == 3
    assert layout["nodes"][0]["position"][2] == 0.0
    assert layout["nodes"][-1]["position"][2] > 0
