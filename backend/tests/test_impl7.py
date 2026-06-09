"""Phase 1.5+ — profiling, architecture export, playground support tests."""
import json


def test_profile_ingest_and_timeline(client) -> None:
    run = client.post("/api/v1/runs", json={"name": "profile-run"})
    run_id = run.json()["id"]

    payload = {
        "events": [
            {
                "epoch": 0,
                "phase": "train",
                "cpu_percent": 45.0,
                "gpu_percent": 88.0,
                "throughput": 1200.0,
                "duration_ms": 500.0,
                "step": 0,
            },
            {
                "epoch": 0,
                "phase": "data_load",
                "cpu_percent": 20.0,
                "gpu_percent": 5.0,
                "throughput": 800.0,
                "duration_ms": 1200.0,
                "step": 0,
            },
            {
                "epoch": 1,
                "phase": "train",
                "cpu_percent": 50.0,
                "gpu_percent": 90.0,
                "throughput": 1300.0,
                "duration_ms": 480.0,
                "step": 100,
            },
        ]
    }
    resp = client.post(f"/api/v1/runs/{run_id}/metrics/profile", json=payload)
    assert resp.status_code == 201
    assert resp.json()["total"] == 3

    listed = client.get(f"/api/v1/runs/{run_id}/metrics/profile")
    assert listed.status_code == 200
    assert listed.json()["total"] == 3

    timeline = client.get(f"/api/v1/runs/{run_id}/metrics/profile/timeline")
    assert timeline.status_code == 200
    body = timeline.json()
    assert body["total_events"] == 3
    assert len(body["epochs"]) == 2
    epoch0 = body["epochs"][0]
    assert epoch0["epoch"] == 0
    assert epoch0["bottleneck_phase"] == "data_load"
    assert any(p["phase"] == "train" for p in epoch0["phases"])


def test_architecture_svg_export(client, minimal_onnx_bytes) -> None:
    imported = client.post(
        "/api/v1/graphs",
        files={"file": ("m.onnx", minimal_onnx_bytes, "application/octet-stream")},
    )
    gid = imported.json()["id"]

    svg = client.get(f"/api/v1/graphs/{gid}/architecture/export?format=svg")
    assert svg.status_code == 200
    assert svg.headers["content-type"].startswith("image/svg+xml")
    assert "<svg" in svg.text
    assert "circle" in svg.text

    png = client.get(f"/api/v1/graphs/{gid}/architecture/export?format=png")
    assert png.status_code in (200, 501)


def test_architecture_svg_service() -> None:
    from app.services.architecture_svg import architecture_to_svg

    arch = {
        "layers": [
            {
                "id": "layer_0",
                "name": "Input",
                "kind": "input",
                "size": 2,
                "nodes": [
                    {"id": "layer_0_n0", "index": 0, "activation": 0.5, "hue": "input"},
                    {"id": "layer_0_n1", "index": 1, "activation": 0.8, "hue": "input"},
                ],
                "bias": {"value": 0.0, "label": "w=0"},
            },
            {
                "id": "layer_1",
                "name": "Output",
                "kind": "output",
                "size": 1,
                "nodes": [
                    {"id": "layer_1_n0", "index": 0, "activation": 0.6, "hue": "output"},
                ],
                "bias": {"value": 0.1, "label": "w=0.1"},
            },
        ],
        "edges": [
            {
                "id": "e0",
                "source": "layer_0_n0",
                "target": "layer_1_n0",
                "weight": 0.5,
                "label": "w=0.5",
            }
        ],
        "formulas": [],
    }
    svg = architecture_to_svg(arch)
    assert svg.startswith("<svg")
    assert "Input" in svg
