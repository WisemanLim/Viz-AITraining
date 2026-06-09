"""Phase 2+ — classical ML charts, PDF export, GAN Lab support tests."""


def test_classical_charts_ingest_and_list(client) -> None:
    run = client.post("/api/v1/runs", json={"name": "sklearn-run"})
    run_id = run.json()["id"]

    payload = {
        "charts": [
            {
                "chart_type": "learning_curve",
                "title": "LR learning curve",
                "data": {
                    "train_sizes": [10, 50, 100],
                    "train_scores": [0.7, 0.85, 0.92],
                    "val_scores": [0.65, 0.8, 0.88],
                },
            },
            {
                "chart_type": "roc",
                "title": "ROC",
                "data": {
                    "fpr": [0.0, 0.2, 1.0],
                    "tpr": [0.0, 0.8, 1.0],
                    "auc": 0.91,
                },
            },
            {
                "chart_type": "confusion_matrix",
                "data": {
                    "labels": ["neg", "pos"],
                    "matrix": [[90, 10], [5, 95]],
                },
            },
            {
                "chart_type": "feature_importance",
                "data": {
                    "features": ["age", "income", "score"],
                    "importances": [0.15, 0.55, 0.3],
                },
            },
        ]
    }
    resp = client.post(f"/api/v1/runs/{run_id}/metrics/classical", json=payload)
    assert resp.status_code == 201
    assert resp.json()["total"] == 4

    listed = client.get(f"/api/v1/runs/{run_id}/metrics/classical")
    assert listed.status_code == 200
    assert listed.json()["total"] == 4

    roc_only = client.get(
        f"/api/v1/runs/{run_id}/metrics/classical?chart_type=roc"
    )
    assert roc_only.status_code == 200
    assert roc_only.json()["total"] == 1
    assert roc_only.json()["items"][0]["data"]["auc"] == 0.91


def test_classical_chart_validation(client) -> None:
    run = client.post("/api/v1/runs", json={"name": "bad-chart"})
    run_id = run.json()["id"]

    bad = client.post(
        f"/api/v1/runs/{run_id}/metrics/classical",
        json={"charts": [{"chart_type": "roc", "data": {"fpr": [0, 1]}}]},
    )
    assert bad.status_code == 422


def test_architecture_pdf_export(client, minimal_onnx_bytes) -> None:
    imported = client.post(
        "/api/v1/graphs",
        files={"file": ("m.onnx", minimal_onnx_bytes, "application/octet-stream")},
    )
    gid = imported.json()["id"]

    pdf = client.get(f"/api/v1/graphs/{gid}/architecture/export?format=pdf")
    assert pdf.status_code in (200, 501)
    if pdf.status_code == 200:
        assert pdf.headers["content-type"] == "application/pdf"
        assert pdf.content[:4] == b"%PDF"
