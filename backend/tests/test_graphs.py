def test_onnx_graph_import_and_get(client, minimal_onnx_bytes) -> None:
    resp = client.post(
        "/api/v1/graphs",
        files={"file": ("tiny.onnx", minimal_onnx_bytes, "application/octet-stream")},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "tiny.onnx"
    assert len(body["nodes"]) >= 2
    assert body["metadata"]["opset_version"] == 13

    graph_id = body["id"]
    get_resp = client.get(f"/api/v1/graphs/{graph_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == graph_id


def test_onnx_graph_list(client, minimal_onnx_bytes) -> None:
    client.post(
        "/api/v1/graphs",
        files={"file": ("m.onnx", minimal_onnx_bytes, "application/octet-stream")},
    )
    listed = client.get("/api/v1/graphs")
    assert listed.status_code == 200
    assert listed.json()["total"] >= 1


def test_onnx_graph_linked_to_run(client, minimal_onnx_bytes) -> None:
    run = client.post("/api/v1/runs", json={"name": "graph-run"})
    run_id = run.json()["id"]

    imported = client.post(
        "/api/v1/graphs",
        data={"run_id": run_id},
        files={"file": ("linked.onnx", minimal_onnx_bytes, "application/octet-stream")},
    )
    assert imported.status_code == 201
    assert imported.json()["run_id"] == run_id

    run_graphs = client.get(f"/api/v1/runs/{run_id}/graphs")
    assert run_graphs.status_code == 200
    assert run_graphs.json()["total"] == 1


def test_onnx_graph_invalid_file(client) -> None:
    resp = client.post(
        "/api/v1/graphs",
        files={"file": ("bad.onnx", b"not-onnx", "application/octet-stream")},
    )
    assert resp.status_code == 422


def test_onnx_graph_wrong_extension(client, minimal_onnx_bytes) -> None:
    resp = client.post(
        "/api/v1/graphs",
        files={"file": ("model.txt", minimal_onnx_bytes, "text/plain")},
    )
    assert resp.status_code == 400


def test_onnx_parser_service(minimal_onnx_bytes) -> None:
    from app.services.onnx_graph import parse_onnx_bytes

    parsed = parse_onnx_bytes(minimal_onnx_bytes)
    op_types = {n["op_type"] for n in parsed["nodes"]}
    assert "Identity" in op_types
    assert "Input" in op_types
    assert len(parsed["edges"]) >= 1
