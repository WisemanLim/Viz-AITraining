"""PyTorch training callback for Viz-AITraining."""
from __future__ import annotations

from typing import Any

from vizaitrain.writer import SummaryWriter


class VizCallback:
    """Logs PyTorch training metrics via SummaryWriter (M6.1 adapter)."""

    def __init__(
        self,
        writer: SummaryWriter | None = None,
        *,
        run_name: str = "pytorch-run",
        api_url: str = "http://localhost:8000",
        params: dict[str, Any] | None = None,
        log_every_n_steps: int = 1,
    ) -> None:
        self._owns_writer = writer is None
        self.writer = writer or SummaryWriter(
            run_name=run_name, api_url=api_url, params=params
        )
        self.log_every_n_steps = max(1, log_every_n_steps)
        self._step = 0

    def on_train_batch_end(
        self,
        *,
        loss: float | None = None,
        metrics: dict[str, float] | None = None,
        step: int | None = None,
    ) -> None:
        self._step = step if step is not None else self._step + 1
        if self._step % self.log_every_n_steps != 0:
            return
        if loss is not None:
            self.writer.add_scalar("loss", float(loss), global_step=self._step)
        if metrics:
            for key, value in metrics.items():
                self.writer.add_scalar(key, float(value), global_step=self._step)

    def on_epoch_end(
        self,
        epoch: int,
        metrics: dict[str, float] | None = None,
    ) -> None:
        step = epoch
        if metrics:
            for key, value in metrics.items():
                self.writer.add_scalar(key, float(value), global_step=step)
        self.writer.flush()

    def close(self) -> None:
        if self._owns_writer:
            self.writer.close()

    def __enter__(self) -> VizCallback:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
