"""Internal training state payload builders (M3.2–M3.5)."""
from __future__ import annotations

from typing import Any


def activation_map_payload(
    width: int,
    height: int,
    values: list[list[float]],
) -> dict[str, Any]:
    return {"width": width, "height": height, "values": values}


def gradient_flow_payload(
    timesteps: list[int],
    layers: list[str],
    magnitudes: list[list[float]],
) -> dict[str, Any]:
    return {"timesteps": timesteps, "layers": layers, "magnitudes": magnitudes}


def embedding_payload(
    points: list[dict[str, Any]],
    *,
    dim: int = 2,
    method: str = "tsne",
) -> dict[str, Any]:
    return {"dim": dim, "method": method, "points": points}


def hidden_state_payload(
    timesteps: list[int],
    states: list[list[float]],
    *,
    cell_index: int | None = None,
) -> dict[str, Any]:
    data: dict[str, Any] = {"timesteps": timesteps, "states": states}
    if cell_index is not None:
        data["cell_index"] = cell_index
    return data
