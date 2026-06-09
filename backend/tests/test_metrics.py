def test_scalar_metrics_ingest_and_list(client) -> None:
    run = client.post("/api/v1/runs", json={"name": "metric-run"})
    run_id = run.json()["id"]

    ingest = client.post(
        f"/api/v1/runs/{run_id}/metrics/scalars",
        json={
            "metrics": [
                {"tag": "loss", "value": 0.9, "step": 0},
                {"tag": "loss", "value": 0.5, "step": 1},
                {"tag": "accuracy", "value": 0.82, "step": 1},
            ]
        },
    )
    assert ingest.status_code == 201
    assert ingest.json()["total"] == 3

    all_metrics = client.get(f"/api/v1/runs/{run_id}/metrics/scalars")
    assert all_metrics.status_code == 200
    assert all_metrics.json()["total"] == 3

    loss_only = client.get(
        f"/api/v1/runs/{run_id}/metrics/scalars", params={"tag": "loss"}
    )
    assert loss_only.json()["total"] == 2


def test_metrics_run_not_found(client) -> None:
    resp = client.post(
        "/api/v1/runs/missing-id/metrics/scalars",
        json={"metrics": [{"tag": "loss", "value": 1.0, "step": 0}]},
    )
    assert resp.status_code == 404
