def test_create_and_list_runs(client) -> None:
    create = client.post(
        "/api/v1/runs",
        json={"name": "exp-001", "params": {"lr": 0.001}},
    )
    assert create.status_code == 201
    body = create.json()
    assert body["name"] == "exp-001"
    assert body["params"] == {"lr": 0.001}
    assert body["status"] == "running"
    run_id = body["id"]

    listing = client.get("/api/v1/runs")
    assert listing.status_code == 200
    assert listing.json()["total"] == 1

    detail = client.get(f"/api/v1/runs/{run_id}")
    assert detail.status_code == 200
    assert detail.json()["id"] == run_id


def test_get_run_not_found(client) -> None:
    resp = client.get("/api/v1/runs/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
