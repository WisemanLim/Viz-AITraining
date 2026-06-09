"""3D layout JSON for neural architecture (M2.3)."""
from __future__ import annotations

from typing import Any

LAYER_Z_GAP = 2.4
NODE_SPREAD = 0.55


def architecture_to_3d(arch: dict[str, Any]) -> dict[str, Any]:
    layers = arch["layers"]
    edges = arch.get("edges", [])

    layer_nodes: list[dict[str, Any]] = []
    node_positions: dict[str, list[float]] = {}

    for li, layer in enumerate(layers):
        z = li * LAYER_Z_GAP
        nodes = layer["nodes"]
        count = max(len(nodes), 1)
        for ni, node in enumerate(nodes):
            y = (ni - (count - 1) / 2) * NODE_SPREAD
            pos = [0.0, y, z]
            node_positions[node["id"]] = pos
            layer_nodes.append(
                {
                    "id": node["id"],
                    "layer_id": layer["id"],
                    "layer_index": li,
                    "index": node["index"],
                    "activation": node.get("activation", 0.5),
                    "hue": node.get("hue", "hidden"),
                    "position": pos,
                }
            )

    layer_blocks = [
        {
            "id": layer["id"],
            "name": layer["name"],
            "kind": layer["kind"],
            "size": layer.get("size", len(layer["nodes"])),
            "position": [0.0, 0.0, li * LAYER_Z_GAP],
        }
        for li, layer in enumerate(layers)
    ]

    edge_lines = []
    for edge in edges:
        s = node_positions.get(edge["source"])
        t = node_positions.get(edge["target"])
        if not s or not t:
            continue
        edge_lines.append(
            {
                "id": edge["id"],
                "source": edge["source"],
                "target": edge["target"],
                "weight": edge.get("weight", 0),
                "points": [s, t],
            }
        )

    bounds_z = max((li * LAYER_Z_GAP for li in range(len(layers))), default=0)
    return {
        "layers": layer_blocks,
        "nodes": layer_nodes,
        "edges": edge_lines,
        "bounds": {"x": 1.5, "y": 2.0, "z": bounds_z + 1.5},
    }
