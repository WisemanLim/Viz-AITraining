def test_histogram_ingest_and_list(client) -> None:
    run = client.post("/api/v1/runs", json={"name": "hist-run"})
    run_id = run.json()["id"]

    ingest = client.post(
        f"/api/v1/runs/{run_id}/metrics/histograms",
        json={
            "histograms": [
                {
                    "tag": "layer1/weights",
                    "bin_edges": [0.0, 0.5, 1.0],
                    "counts": [3.0, 7.0],
                    "step": 0,
                },
                {
                    "tag": "layer1/weights",
                    "bin_edges": [0.0, 0.5, 1.0],
                    "counts": [5.0, 5.0],
                    "step": 1,
                },
            ]
        },
    )
    assert ingest.status_code == 201
    body = ingest.json()
    assert body["total"] == 2
    assert body["items"][0]["bin_edges"] == [0.0, 0.5, 1.0]
    assert body["items"][0]["counts"] == [3.0, 7.0]

    listed = client.get(f"/api/v1/runs/{run_id}/metrics/histograms")
    assert listed.status_code == 200
    assert listed.json()["total"] == 2

    filtered = client.get(
        f"/api/v1/runs/{run_id}/metrics/histograms",
        params={"tag": "layer1/weights"},
    )
    assert filtered.json()["total"] == 2


def test_histogram_validation(client) -> None:
    run = client.post("/api/v1/runs", json={"name": "bad-hist"})
    run_id = run.json()["id"]

    resp = client.post(
        f"/api/v1/runs/{run_id}/metrics/histograms",
        json={
            "histograms": [
                {
                    "tag": "bad",
                    "bin_edges": [0.0, 1.0],
                    "counts": [1.0, 2.0],
                    "step": 0,
                }
            ]
        },
    )
    assert resp.status_code == 422


def test_histogram_run_not_found(client) -> None:
    resp = client.post(
        "/api/v1/runs/missing-id/metrics/histograms",
        json={
            "histograms": [
                {
                    "tag": "w",
                    "bin_edges": [0.0, 1.0],
                    "counts": [1.0],
                    "step": 0,
                }
            ]
        },
    )
    assert resp.status_code == 404
