"""SummaryWriter-compatible logger for Viz-AITraining API."""
from __future__ import annotations

from typing import Any

import httpx


def _linear_histogram(
    values: list[float], num_bins: int
) -> tuple[list[float], list[float]]:
    if not values:
        raise ValueError("values must not be empty")
    if num_bins < 1:
        raise ValueError("num_bins must be >= 1")
    lo, hi = min(values), max(values)
    if lo == hi:
        hi = lo + 1.0
    width = (hi - lo) / num_bins
    edges = [lo + i * width for i in range(num_bins + 1)]
    counts = [0.0] * num_bins
    for v in values:
        if v >= hi:
            idx = num_bins - 1
        else:
            idx = min(int((v - lo) / width), num_bins - 1)
        counts[idx] += 1.0
    return edges, counts


class SummaryWriter:
    """Logs scalars and histograms to Viz-AITraining backend (TensorBoard subset)."""

    def __init__(
        self,
        run_id: str | None = None,
        run_name: str = "default",
        api_url: str = "http://localhost:8000",
        params: dict[str, Any] | None = None,
    ) -> None:
        self.api_url = api_url.rstrip("/")
        self._client = httpx.Client(base_url=self.api_url, timeout=10.0)
        self._scalar_buffer: list[dict[str, Any]] = []
        self._histogram_buffer: list[dict[str, Any]] = []
        self._profile_buffer: list[dict[str, Any]] = []
        self._classical_buffer: list[dict[str, Any]] = []
        self._internal_buffer: list[dict[str, Any]] = []
        self._xai_buffer: list[dict[str, Any]] = []
        self.run_id = run_id or self._create_run(run_name, params)

    def _create_run(self, name: str, params: dict[str, Any] | None) -> str:
        payload: dict[str, Any] = {"name": name}
        if params:
            payload["params"] = params
        resp = self._client.post("/api/v1/runs", json=payload)
        resp.raise_for_status()
        return resp.json()["id"]

    def add_scalar(
        self,
        tag: str,
        scalar_value: float,
        global_step: int | None = None,
    ) -> None:
        self._scalar_buffer.append(
            {"tag": tag, "value": scalar_value, "step": global_step}
        )

    def add_histogram(
        self,
        tag: str,
        bin_edges: list[float],
        counts: list[float],
        global_step: int | None = None,
    ) -> None:
        self._histogram_buffer.append(
            {
                "tag": tag,
                "bin_edges": bin_edges,
                "counts": counts,
                "step": global_step,
            }
        )

    def add_histogram_from_values(
        self,
        tag: str,
        values: list[float],
        bins: int = 30,
        global_step: int | None = None,
    ) -> None:
        edges, counts = _linear_histogram(values, bins)
        self.add_histogram(tag, edges, counts, global_step)

    def add_profile(
        self,
        phase: str,
        epoch: int,
        *,
        cpu_percent: float | None = None,
        gpu_percent: float | None = None,
        memory_mb: float | None = None,
        throughput: float | None = None,
        duration_ms: float | None = None,
        step: int | None = None,
    ) -> None:
        """Log a training profile event (M1.3)."""
        self._profile_buffer.append(
            {
                "epoch": epoch,
                "phase": phase,
                "cpu_percent": cpu_percent,
                "gpu_percent": gpu_percent,
                "memory_mb": memory_mb,
                "throughput": throughput,
                "duration_ms": duration_ms,
                "step": step,
            }
        )

    def add_classical_chart(
        self,
        chart_type: str,
        data: dict[str, Any],
        title: str | None = None,
    ) -> None:
        """Log a classical ML diagnostic chart (M1.4)."""
        self._classical_buffer.append(
            {"chart_type": chart_type, "title": title, "data": data}
        )

    def add_learning_curve(
        self,
        train_sizes: list[int | float],
        train_scores: list[float],
        val_scores: list[float],
        title: str | None = "Learning curve",
    ) -> None:
        from vizaitrain.classical import learning_curve_payload

        self.add_classical_chart(
            "learning_curve",
            learning_curve_payload(train_sizes, train_scores, val_scores),
            title=title,
        )

    def add_roc_curve(
        self,
        fpr: list[float],
        tpr: list[float],
        auc: float | None = None,
        title: str | None = "ROC curve",
    ) -> None:
        from vizaitrain.classical import roc_payload

        self.add_classical_chart("roc", roc_payload(fpr, tpr, auc), title=title)

    def add_confusion_matrix(
        self,
        labels: list[str],
        matrix: list[list[int | float]],
        title: str | None = "Confusion matrix",
    ) -> None:
        from vizaitrain.classical import confusion_matrix_payload

        self.add_classical_chart(
            "confusion_matrix",
            confusion_matrix_payload(labels, matrix),
            title=title,
        )

    def add_feature_importance(
        self,
        features: list[str],
        importances: list[float],
        title: str | None = "Feature importance",
    ) -> None:
        from vizaitrain.classical import feature_importance_payload

        self.add_classical_chart(
            "feature_importance",
            feature_importance_payload(features, importances),
            title=title,
        )

    def add_internal_metric(
        self,
        kind: str,
        data: dict[str, Any],
        *,
        layer: str | None = None,
        step: int | None = None,
        epoch: int | None = None,
        title: str | None = None,
    ) -> None:
        """Log internal training state (M3.2–M3.5)."""
        self._internal_buffer.append(
            {
                "kind": kind,
                "layer": layer,
                "step": step,
                "epoch": epoch,
                "title": title,
                "data": data,
            }
        )

    def add_activation_map(
        self,
        layer: str,
        width: int,
        height: int,
        values: list[list[float]],
        *,
        step: int | None = None,
        title: str | None = None,
    ) -> None:
        from vizaitrain.internal import activation_map_payload

        self.add_internal_metric(
            "activation_map",
            activation_map_payload(width, height, values),
            layer=layer,
            step=step,
            title=title or f"{layer} activation",
        )

    def add_gradient_flow(
        self,
        timesteps: list[int],
        layers: list[str],
        magnitudes: list[list[float]],
        *,
        step: int | None = None,
        title: str | None = "Gradient flow",
    ) -> None:
        from vizaitrain.internal import gradient_flow_payload

        self.add_internal_metric(
            "gradient_flow",
            gradient_flow_payload(timesteps, layers, magnitudes),
            step=step,
            title=title,
        )

    def add_embedding(
        self,
        points: list[dict[str, Any]],
        *,
        method: str = "tsne",
        dim: int = 2,
        step: int | None = None,
        title: str | None = None,
    ) -> None:
        from vizaitrain.internal import embedding_payload

        self.add_internal_metric(
            "embedding",
            embedding_payload(points, dim=dim, method=method),
            step=step,
            title=title or f"{method} embedding",
        )

    def add_hidden_state(
        self,
        timesteps: list[int],
        states: list[list[float]],
        *,
        cell_index: int | None = None,
        title: str | None = "Hidden state",
    ) -> None:
        from vizaitrain.internal import hidden_state_payload

        self.add_internal_metric(
            "hidden_state",
            hidden_state_payload(timesteps, states, cell_index=cell_index),
            title=title,
        )

    def add_xai_attribution(
        self,
        method: str,
        scope: str,
        data: dict[str, Any],
        *,
        step: int | None = None,
        epoch: int | None = None,
        title: str | None = None,
    ) -> None:
        """Log SHAP/LIME attribution (M4)."""
        self._xai_buffer.append(
            {
                "method": method,
                "scope": scope,
                "step": step,
                "epoch": epoch,
                "title": title,
                "data": data,
            }
        )

    def add_shap_local(
        self,
        features: list[str],
        values: list[float],
        *,
        prediction: float | None = None,
        title: str | None = "SHAP local",
    ) -> None:
        from vizaitrain.xai import local_attribution_payload

        self.add_xai_attribution(
            "shap",
            "local",
            local_attribution_payload(features, values, prediction=prediction),
            title=title,
        )

    def add_lime_local(
        self,
        features: list[str],
        values: list[float],
        *,
        prediction: float | None = None,
        title: str | None = "LIME local",
    ) -> None:
        from vizaitrain.xai import local_attribution_payload

        self.add_xai_attribution(
            "lime",
            "local",
            local_attribution_payload(features, values, prediction=prediction),
            title=title,
        )

    def add_shap_global(
        self,
        features: list[str],
        values: list[float],
        *,
        title: str | None = "SHAP global",
    ) -> None:
        from vizaitrain.xai import global_attribution_payload

        self.add_xai_attribution(
            "shap",
            "global",
            global_attribution_payload(features, values),
            title=title,
        )

    def add_shap_temporal(
        self,
        steps: list[int],
        features: list[str],
        values_over_time: list[list[float]],
        *,
        title: str | None = "SHAP temporal",
    ) -> None:
        from vizaitrain.xai import temporal_attribution_payload

        self.add_xai_attribution(
            "shap",
            "temporal",
            temporal_attribution_payload(steps, features, values_over_time),
            title=title,
        )

    def flush(self) -> None:
        if not self.run_id:
            return
        if self._scalar_buffer:
            resp = self._client.post(
                f"/api/v1/runs/{self.run_id}/metrics/scalars",
                json={"metrics": self._scalar_buffer},
            )
            resp.raise_for_status()
            self._scalar_buffer.clear()
        if self._histogram_buffer:
            resp = self._client.post(
                f"/api/v1/runs/{self.run_id}/metrics/histograms",
                json={"histograms": self._histogram_buffer},
            )
            resp.raise_for_status()
            self._histogram_buffer.clear()
        if self._profile_buffer:
            resp = self._client.post(
                f"/api/v1/runs/{self.run_id}/metrics/profile",
                json={"events": list(self._profile_buffer)},
            )
            resp.raise_for_status()
            self._profile_buffer.clear()
        if self._classical_buffer:
            resp = self._client.post(
                f"/api/v1/runs/{self.run_id}/metrics/classical",
                json={"charts": list(self._classical_buffer)},
            )
            resp.raise_for_status()
            self._classical_buffer.clear()
        if self._internal_buffer:
            resp = self._client.post(
                f"/api/v1/runs/{self.run_id}/metrics/internal",
                json={"metrics": list(self._internal_buffer)},
            )
            resp.raise_for_status()
            self._internal_buffer.clear()
        if self._xai_buffer:
            resp = self._client.post(
                f"/api/v1/runs/{self.run_id}/metrics/xai",
                json={"attributions": list(self._xai_buffer)},
            )
            resp.raise_for_status()
            self._xai_buffer.clear()

    def close(self) -> None:
        try:
            self.flush()
        finally:
            self._client.close()

    def __enter__(self) -> SummaryWriter:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
