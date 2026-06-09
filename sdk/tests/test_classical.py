"""Tests for classical ML chart logging (M1.4)."""
from unittest.mock import MagicMock

from vizaitrain.writer import SummaryWriter


def test_add_classical_charts_flush() -> None:
    writer = SummaryWriter(run_id="run-1", api_url="http://test")
    writer._client = MagicMock()
    writer._client.post.return_value.status_code = 201
    writer._client.post.return_value.raise_for_status = MagicMock()

    writer.add_learning_curve([10, 50], [0.7, 0.9], [0.65, 0.85])
    writer.add_roc_curve([0.0, 1.0], [0.0, 1.0], auc=0.95)
    writer.flush()

    calls = [c for c in writer._client.post.call_args_list if "classical" in c[0][0]]
    assert len(calls) == 1
    charts = calls[0].kwargs["json"]["charts"]
    assert len(charts) == 2
    assert charts[0]["chart_type"] == "learning_curve"
    assert charts[1]["data"]["auc"] == 0.95
