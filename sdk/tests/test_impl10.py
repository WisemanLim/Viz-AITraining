"""Tests for Phase 4+ XAI adapters (no shap required for payload tests)."""
from unittest.mock import MagicMock

from vizaitrain.writer import SummaryWriter
from vizaitrain.xai_adapter import (
    from_shap_temporal_checkpoints,
    from_shap_values,
    from_sklearn_permutation_importance,
    log_shap_temporal_from_checkpoints,
)


def test_from_shap_values_payload() -> None:
    payload = from_shap_values(
        ["age", "income"],
        [0.3, -0.1],
        prediction=0.82,
        base_value=0.5,
    )
    assert payload["features"] == ["age", "income"]
    assert payload["values"] == [0.3, -0.1]
    assert payload["prediction"] == 0.82
    assert payload["base_value"] == 0.5


def test_from_shap_temporal_checkpoints() -> None:
    payload = from_shap_temporal_checkpoints(
        [(0, [0.1, 0.2]), (100, [0.25, 0.05])],
        ["f0", "f1"],
    )
    assert payload["steps"] == [0, 100]
    assert payload["values_over_time"] == [[0.1, 0.2], [0.25, 0.05]]


def test_from_sklearn_permutation_importance() -> None:
    payload = from_sklearn_permutation_importance(
        ["a", "b"],
        [0.4, 0.1],
    )
    assert payload["values"] == [0.4, 0.1]


def test_writer_add_shap_temporal_flush() -> None:
    writer = SummaryWriter(run_id="run-1", api_url="http://test")
    writer._client = MagicMock()
    writer._client.post.return_value.status_code = 201
    writer._client.post.return_value.raise_for_status = MagicMock()

    writer.add_shap_temporal(
        [0, 50, 100],
        ["x", "y"],
        [[0.1, 0.2], [0.15, 0.18], [0.22, 0.09]],
    )
    writer.add_shap_global(["x", "y"], [0.5, 0.3])
    writer.flush()

    paths = [c[0][0] for c in writer._client.post.call_args_list]
    assert any("xai" in p for p in paths)
    body = writer._client.post.call_args_list[0][1]["json"]
    assert len(body["attributions"]) == 2
    assert body["attributions"][0]["scope"] == "temporal"
    assert body["attributions"][1]["scope"] == "global"


def test_log_shap_temporal_from_checkpoints() -> None:
    writer = SummaryWriter(run_id="run-1", api_url="http://test")
    writer._client = MagicMock()
    writer._client.post.return_value.status_code = 201
    writer._client.post.return_value.raise_for_status = MagicMock()

    log_shap_temporal_from_checkpoints(
        writer,
        [(0, [0.1]), (10, [0.3])],
        ["feat"],
        flush=True,
    )
    assert writer._client.post.called
