"""SDK callback tests (no PyTorch required)."""
from unittest.mock import MagicMock

from vizaitrain.callbacks.pytorch import VizCallback


def test_viz_callback_logs_scalars() -> None:
    writer = MagicMock()
    cb = VizCallback(writer=writer, log_every_n_steps=1)
    cb.on_train_batch_end(loss=0.5, metrics={"accuracy": 0.9}, step=1)
    writer.add_scalar.assert_any_call("loss", 0.5, global_step=1)
    writer.add_scalar.assert_any_call("accuracy", 0.9, global_step=1)


def test_viz_callback_epoch_flush() -> None:
    writer = MagicMock()
    cb = VizCallback(writer=writer)
    cb.on_epoch_end(3, metrics={"val_loss": 0.2})
    writer.add_scalar.assert_called_with("val_loss", 0.2, global_step=3)
    writer.flush.assert_called_once()
