"""Demo seed endpoint tests."""

def test_demo_seed_creates_run(client) -> None:
    empty = client.get("/api/v1/runs")
    assert empty.json()["total"] == 0

    resp = client.post("/api/v1/demo/seed")
    assert resp.status_code == 200
    body = resp.json()
    assert body["run_id"]
    assert body["scalars"] >= 6

    listed = client.get("/api/v1/runs")
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["name"] == "demo-experiment"

    run_id = body["run_id"]
    scalars = client.get(f"/api/v1/runs/{run_id}/metrics/scalars")
    assert scalars.json()["total"] >= 6

    xai = client.get(f"/api/v1/runs/{run_id}/metrics/xai")
    assert xai.json()["total"] >= 1
