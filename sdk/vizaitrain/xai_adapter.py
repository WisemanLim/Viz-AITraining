"""Optional sklearn / SHAP / LIME adapters for XAI logging (M4, Phase 4+)."""
from __future__ import annotations

from typing import Any, Sequence

from vizaitrain.xai import (
    global_attribution_payload,
    local_attribution_payload,
    temporal_attribution_payload,
)


def _as_list(values: Any) -> list[float]:
    if hasattr(values, "tolist"):
        return [float(x) for x in values.tolist()]
    return [float(x) for x in values]


def from_shap_values(
    feature_names: list[str],
    shap_values: Any,
    *,
    prediction: float | None = None,
    base_value: float | None = None,
) -> dict[str, Any]:
    """Build local SHAP payload from a 1-D attribution vector."""
    vals = _as_list(shap_values)
    if len(vals) != len(feature_names):
        raise ValueError("shap_values length must match feature_names")
    return local_attribution_payload(
        feature_names,
        vals,
        prediction=prediction,
        base_value=base_value,
    )


def from_sklearn_permutation_importance(
    feature_names: list[str],
    importances: Any,
) -> dict[str, Any]:
    """Global attribution from sklearn.inspection.permutation_importance."""
    return global_attribution_payload(feature_names, _as_list(importances))


def from_sklearn_feature_importances_global(
    feature_names: list[str],
    model: Any,
) -> dict[str, Any]:
    """Tree/ensemble global importances via ``feature_importances_``."""
    if not hasattr(model, "feature_importances_"):
        raise TypeError("model has no feature_importances_ attribute")
    return global_attribution_payload(
        feature_names,
        _as_list(model.feature_importances_),
    )


def from_shap_temporal_checkpoints(
    checkpoints: Sequence[tuple[int, list[float]]],
    feature_names: list[str],
) -> dict[str, Any]:
    """Temporal payload from ``[(step, shap_vector), ...]``."""
    steps = [int(s) for s, _ in checkpoints]
    values_over_time = [_as_list(v) for _, v in checkpoints]
    for row in values_over_time:
        if len(row) != len(feature_names):
            raise ValueError("each checkpoint vector must match feature_names")
    return temporal_attribution_payload(steps, feature_names, values_over_time)


def explain_shap_local(
    model: Any,
    X: Any,
    *,
    feature_names: list[str] | None = None,
    sample_index: int = 0,
) -> dict[str, Any]:
    """Compute local SHAP for one row (requires ``shap`` optional extra)."""
    import shap  # noqa: PLC0415 — optional dependency

    if feature_names is None:
        if hasattr(X, "columns"):
            feature_names = list(X.columns)
        else:
            feature_names = [f"f{i}" for i in range(X.shape[1])]

    row = X.iloc[[sample_index]] if hasattr(X, "iloc") else X[sample_index : sample_index + 1]
    explainer = shap.Explainer(model, X if hasattr(X, "iloc") else X)
    explanation = explainer(row)
    values = explanation.values[0]
    if getattr(values, "ndim", 1) > 1:
        values = values.sum(axis=-1)
    pred = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(row)
        pred = float(proba[0, -1]) if proba.ndim > 1 else float(proba[0])
    elif hasattr(model, "predict"):
        pred = float(model.predict(row)[0])
    base = None
    if hasattr(explanation, "base_values"):
        bv = explanation.base_values[0]
        base = float(bv) if not hasattr(bv, "__len__") else float(bv.flat[0])
    return from_shap_values(
        feature_names,
        values,
        prediction=pred,
        base_value=base,
    )


def explain_shap_global(
    model: Any,
    X: Any,
    *,
    feature_names: list[str] | None = None,
    max_samples: int = 100,
) -> dict[str, Any]:
    """Mean |SHAP| across samples as global attribution."""
    import shap  # noqa: PLC0415

    if feature_names is None:
        if hasattr(X, "columns"):
            feature_names = list(X.columns)
        else:
            feature_names = [f"f{i}" for i in range(X.shape[1])]

    sample = X
    if hasattr(X, "iloc") and len(X) > max_samples:
        sample = X.iloc[:max_samples]
    elif len(X) > max_samples:
        sample = X[:max_samples]

    explainer = shap.Explainer(model, sample)
    explanation = explainer(sample)
    import numpy as np

    mean_abs = np.abs(explanation.values).mean(axis=0)
    if mean_abs.ndim > 1:
        mean_abs = mean_abs.sum(axis=-1)
    return global_attribution_payload(feature_names, _as_list(mean_abs))


def explain_shap_temporal(
    model_factory: Any,
    X: Any,
    checkpoints: Sequence[int],
    *,
    feature_names: list[str] | None = None,
    sample_index: int = 0,
) -> dict[str, Any]:
    """SHAP over training checkpoints: ``model_factory(step) -> fitted model``."""
    import shap  # noqa: PLC0415

    if feature_names is None:
        if hasattr(X, "columns"):
            feature_names = list(X.columns)
        else:
            feature_names = [f"f{i}" for i in range(X.shape[1])]

    row = X.iloc[[sample_index]] if hasattr(X, "iloc") else X[sample_index : sample_index + 1]
    series: list[tuple[int, list[float]]] = []
    for step in checkpoints:
        model = model_factory(step)
        explainer = shap.Explainer(model, X if hasattr(X, "iloc") else X)
        explanation = explainer(row)
        values = explanation.values[0]
        if getattr(values, "ndim", 1) > 1:
            import numpy as np

            values = np.abs(values).sum(axis=-1)
        series.append((int(step), _as_list(values)))
    return from_shap_temporal_checkpoints(series, feature_names)


def log_shap_local_from_model(
    writer: Any,
    model: Any,
    X: Any,
    *,
    feature_names: list[str] | None = None,
    sample_index: int = 0,
    title: str | None = "SHAP local (auto)",
    flush: bool = False,
) -> None:
    """Convenience: compute + log local SHAP via SummaryWriter."""
    payload = explain_shap_local(
        model, X, feature_names=feature_names, sample_index=sample_index
    )
    writer.add_xai_attribution("shap", "local", payload, title=title)
    if flush:
        writer.flush()


def log_shap_global_from_model(
    writer: Any,
    model: Any,
    X: Any,
    *,
    feature_names: list[str] | None = None,
    title: str | None = "SHAP global (auto)",
    flush: bool = False,
) -> None:
    payload = explain_shap_global(model, X, feature_names=feature_names)
    writer.add_xai_attribution("shap", "global", payload, title=title)
    if flush:
        writer.flush()


def log_shap_temporal_from_checkpoints(
    writer: Any,
    checkpoints: Sequence[tuple[int, list[float]]],
    feature_names: list[str],
    *,
    title: str | None = "SHAP temporal (auto)",
    flush: bool = False,
) -> None:
    payload = from_shap_temporal_checkpoints(checkpoints, feature_names)
    writer.add_xai_attribution("shap", "temporal", payload, title=title)
    if flush:
        writer.flush()
