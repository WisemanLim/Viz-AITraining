"""ONNX / graph JSON → MLP-style layer architecture for neural-network visualization."""
from __future__ import annotations

from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper

MAX_VIZ_NODES = 16


def _fmt_weight(value: float) -> str:
    return f"w={value:.2g}"


def _subsample_indices(size: int, max_nodes: int) -> list[int]:
    if size <= max_nodes:
        return list(range(size))
    return [int(round(i * (size - 1) / (max_nodes - 1))) for i in range(max_nodes)]


def _build_mlp_layers(
    layer_sizes: list[int],
    layer_names: list[str],
    weight_matrices: list[np.ndarray],
    bias_vectors: list[np.ndarray | None],
) -> dict[str, Any]:
    layers: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    connections: list[dict[str, Any]] = []

    viz_indices = [_subsample_indices(s, MAX_VIZ_NODES) for s in layer_sizes]

    for li, size in enumerate(layer_sizes):
        layer_id = f"layer_{li}"
        is_input = li == 0
        is_output = li == len(layer_sizes) - 1
        nodes = []
        for ni in viz_indices[li]:
            nid = f"{layer_id}_n{ni}"
            activation = 0.3 + 0.7 * (ni / max(size - 1, 1))
            hue = "input" if is_input else ("output" if is_output else "hidden")
            nodes.append(
                {
                    "id": nid,
                    "index": ni,
                    "activation": round(activation, 2),
                    "hue": hue,
                }
            )
        bias_val = 0.0
        if li > 0 and li - 1 < len(bias_vectors):
            b = bias_vectors[li - 1]
            if b is not None and len(b) > 0:
                bias_val = float(b[0])
        layers.append(
            {
                "id": layer_id,
                "name": layer_names[li] if li < len(layer_names) else f"Layer {li}",
                "kind": "input" if is_input else ("output" if is_output else "hidden"),
                "nodes": nodes,
                "size": size,
                "bias": {"value": bias_val, "label": _fmt_weight(bias_val)},
            }
        )

    edge_idx = 0
    for li in range(len(layer_sizes) - 1):
        matrix = weight_matrices[li] if li < len(weight_matrices) else None
        if matrix is not None:
            mat = np.asarray(matrix, dtype=float)
            connections.append(
                {
                    "id": f"conn_{li}_{li + 1}",
                    "from_layer": li,
                    "to_layer": li + 1,
                    "matrix": mat.tolist(),
                    "shape": [int(mat.shape[0]), int(mat.shape[1])],
                }
            )
        src_layer = layers[li]
        dst_layer = layers[li + 1]
        for sn in src_layer["nodes"]:
            for dn in dst_layer["nodes"]:
                si, di = sn["index"], dn["index"]
                if matrix is not None and mat.shape == (layer_sizes[li + 1], layer_sizes[li]):
                    w = float(mat[di, si])
                elif matrix is not None and mat.ndim == 2:
                    w = float(mat.flat[(di * mat.shape[1] + si) % mat.size])
                else:
                    w = 0.5
                edges.append(
                    {
                        "id": f"edge_{edge_idx}",
                        "source": sn["id"],
                        "target": dn["id"],
                        "weight": w,
                        "label": _fmt_weight(w),
                        "source_index": si,
                        "target_index": di,
                    }
                )
                edge_idx += 1

    return {
        "layers": layers,
        "edges": edges,
        "connections": connections,
        "formulas": [
            {"id": "sum", "text": "y = f(Σ wᵢxᵢ + b)", "x": 0.05, "y": 0.08},
            {"id": "sigmoid", "text": "σ(x) = 1 / (1 + e⁻ˣ)", "x": 0.72, "y": 0.12},
        ],
    }


def _gemm_layers(
    model: onnx.ModelProto,
) -> list[tuple[str, int, int, np.ndarray, np.ndarray | None]]:
    initializers = {
        init.name: numpy_helper.to_array(init) for init in model.graph.initializer
    }
    results: list[tuple[str, int, int, np.ndarray, np.ndarray | None]] = []

    for idx, node in enumerate(model.graph.node):
        if node.op_type not in ("Gemm", "MatMul"):
            continue
        weight_name = next((inp for inp in node.input if inp in initializers), None)
        if weight_name is None:
            continue
        arr = np.asarray(initializers[weight_name], dtype=float)
        if arr.ndim != 2:
            continue
        out_dim, in_dim = int(arr.shape[0]), int(arr.shape[1])
        bias: np.ndarray | None = None
        for inp in node.input:
            if inp in initializers and inp != weight_name:
                b = np.asarray(initializers[inp], dtype=float)
                if b.ndim == 1:
                    bias = b
                    break
        name = node.name or f"{node.op_type}_{idx}"
        results.append((name, in_dim, out_dim, arr, bias))
    return results


def _demo_architecture() -> dict[str, Any]:
    sizes = [5, 6, 6, 4]
    names = ["Input Data", "Hidden 1", "Hidden 2", "Output"]
    matrices = [
        np.array(
            [
                [0.75, -1.2, 0.5, 2.7, -0.3],
                [0.14, 0.8, -0.6, 1.1, 0.2],
                [0.5, -0.9, 1.4, 0.3, -1.0],
                [0.75, -1.2, 0.5, 2.7, -0.3],
                [0.14, 0.8, -0.6, 1.1, 0.2],
                [-1.6, 0.4, 0.9, -0.2, 0.7],
            ]
        ),
        np.random.default_rng(42).standard_normal((6, 6)),
        np.random.default_rng(43).standard_normal((4, 6)),
    ]
    biases = [np.array([0.14, -1.2, 0.5, 2.7, -0.3, -1.6]), np.array([0.75, -1.2, 0.5, 2.7, -0.3, -1.6]), None]
    return _build_mlp_layers(sizes, names, matrices, biases)


def parse_architecture_from_bytes(data: bytes) -> dict[str, Any]:
    model = onnx.load_model_from_string(data)
    gemms = _gemm_layers(model)

    if gemms:
        sizes = [gemms[0][1]]
        names = ["Input Data"]
        matrices: list[np.ndarray] = []
        biases: list[np.ndarray | None] = []
        for i, (gname, _in_dim, out_dim, matrix, bias) in enumerate(gemms):
            sizes.append(out_dim)
            matrices.append(matrix)
            biases.append(bias)
            if i < len(gemms) - 1:
                names.append(gname)
        names.append("Output")
        return _build_mlp_layers(sizes, names, matrices, biases)

    return _demo_architecture()


def _infer_sizes_from_graph_json(parsed: dict[str, Any]) -> list[int]:
    sizes: list[int] = []
    names: list[str] = []
    nodes = parsed.get("nodes", [])

    for node in nodes:
        if node.get("op_type") != "Input":
            continue
        shape = node.get("shape")
        if not shape:
            continue
        dims = [d for d in shape if isinstance(d, int) and d > 0]
        if not dims:
            continue
        feat = int(dims[-1]) if len(dims) > 1 else int(dims[0])
        if feat > 0:
            sizes.append(feat)
            names.append(node.get("label") or "Input Data")
            break

    for node in nodes:
        if node.get("op_type") not in ("Gemm", "MatMul"):
            continue
        shape = node.get("shape")
        if shape and isinstance(shape[-1], int):
            sizes.append(int(shape[-1]))
            names.append(node.get("label") or node.get("op_type", "Layer"))
        elif sizes:
            sizes.append(max(4, min(sizes[-1], MAX_VIZ_NODES)))

    if not sizes:
        return [5, 6, 4]

    if len(sizes) == 1:
        sizes.extend([6, sizes[0]])
        names.extend(["Hidden", "Output"])
    elif names and names[-1] != "Output":
        names.append("Output")

    return sizes


def parse_architecture_from_graph_json(parsed: dict[str, Any]) -> dict[str, Any]:
    """Fallback for legacy graphs without stored ONNX artifact."""
    sizes = _infer_sizes_from_graph_json(parsed)
    names = ["Input Data"]
    for i in range(1, len(sizes) - 1):
        names.append(f"Hidden {i}")
    if len(sizes) > 1:
        names.append("Output")

    rng = np.random.default_rng(7)
    matrices = []
    biases: list[np.ndarray | None] = []
    for i in range(len(sizes) - 1):
        out_d, in_d = sizes[i + 1], sizes[i]
        matrices.append(rng.standard_normal((out_d, in_d)) * 0.5)
        biases.append(rng.standard_normal(out_d) * 0.1)

    return _build_mlp_layers(sizes, names, matrices, biases)
