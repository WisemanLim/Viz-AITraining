"""Classical ML chart payload builders (M1.4)."""
from __future__ import annotations

from typing import Any


def learning_curve_payload(
    train_sizes: list[int | float],
    train_scores: list[float],
    val_scores: list[float],
) -> dict[str, Any]:
    return {
        "train_sizes": train_sizes,
        "train_scores": train_scores,
        "val_scores": val_scores,
    }


def roc_payload(
    fpr: list[float],
    tpr: list[float],
    auc: float | None = None,
) -> dict[str, Any]:
    data: dict[str, Any] = {"fpr": fpr, "tpr": tpr}
    if auc is not None:
        data["auc"] = auc
    return data


def confusion_matrix_payload(
    labels: list[str],
    matrix: list[list[int | float]],
) -> dict[str, Any]:
    return {"labels": labels, "matrix": matrix}


def feature_importance_payload(
    features: list[str],
    importances: list[float],
) -> dict[str, Any]:
    return {"features": features, "importances": importances}
