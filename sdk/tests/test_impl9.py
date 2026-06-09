"""Tests for internal state and XAI logging (Phase 3+)."""
from unittest.mock import MagicMock

from vizaitrain.writer import SummaryWriter


def test_add_internal_and_xai_flush() -> None:
    writer = SummaryWriter(run_id="run-1", api_url="http://test")
    writer._client = MagicMock()
    writer._client.post.return_value.status_code = 201
    writer._client.post.return_value.raise_for_status = MagicMock()

    writer.add_activation_map("conv1", 2, 2, [[0.1, 0.2], [0.3, 0.4]])
    writer.add_shap_local(["a", "b"], [0.2, -0.1], prediction=0.9)
    writer.flush()

    paths = [c[0][0] for c in writer._client.post.call_args_list]
    assert any("internal" in p for p in paths)
    assert any("xai" in p for p in paths)
