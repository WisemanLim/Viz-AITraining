"""Optional scikit-learn adapter for classical ML charts (M1.4)."""
from __future__ import annotations

from typing import Any

from vizaitrain.classical import (
    confusion_matrix_payload,
    feature_importance_payload,
    learning_curve_payload,
    roc_payload,
)


def from_sklearn_learning_curve(
    train_sizes: Any,
    train_scores: Any,
    val_scores: Any,
) -> dict[str, Any]:
    """Build learning_curve payload from sklearn.model_selection.learning_curve output."""
    return learning_curve_payload(
        train_sizes.tolist(),
        train_scores.mean(axis=1).tolist(),
        val_scores.mean(axis=1).tolist(),
    )


def from_sklearn_roc(
    fpr: Any,
    tpr: Any,
    auc: float | None = None,
) -> dict[str, Any]:
    """Build roc payload from sklearn.metrics.roc_curve output."""
    return roc_payload(fpr.tolist(), tpr.tolist(), auc=auc)


def from_sklearn_confusion_matrix(
    labels: list[str],
    matrix: Any,
) -> dict[str, Any]:
    return confusion_matrix_payload(labels, matrix.tolist())


def from_sklearn_feature_importances(
    feature_names: list[str],
    importances: Any,
) -> dict[str, Any]:
    return feature_importance_payload(feature_names, importances.tolist())
