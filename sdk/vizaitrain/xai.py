"""XAI attribution payload builders (M4)."""
from __future__ import annotations

from typing import Any


def local_attribution_payload(
    features: list[str],
    values: list[float],
    *,
    prediction: float | None = None,
    base_value: float | None = None,
) -> dict[str, Any]:
    data: dict[str, Any] = {"features": features, "values": values}
    if prediction is not None:
        data["prediction"] = prediction
    if base_value is not None:
        data["base_value"] = base_value
    return data


def global_attribution_payload(
    features: list[str],
    values: list[float],
) -> dict[str, Any]:
    return {"features": features, "values": values}


def temporal_attribution_payload(
    steps: list[int],
    features: list[str],
    values_over_time: list[list[float]],
) -> dict[str, Any]:
    return {
        "steps": steps,
        "features": features,
        "values_over_time": values_over_time,
    }
