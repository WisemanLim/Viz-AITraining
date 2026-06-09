"""SDK profile logging tests."""
from unittest.mock import MagicMock

from vizaitrain.writer import SummaryWriter


def test_add_profile_flush() -> None:
    writer = SummaryWriter(run_id="test-run")
    writer._client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    writer._client.post.return_value = mock_resp

    writer.add_profile(
        "train",
        epoch=1,
        cpu_percent=40.0,
        gpu_percent=85.0,
        throughput=1000.0,
        duration_ms=500.0,
        step=10,
    )
    writer.flush()

    writer._client.post.assert_called_once()
    args, kwargs = writer._client.post.call_args
    assert args[0].endswith("/metrics/profile")
    assert kwargs["json"]["events"][0]["phase"] == "train"
