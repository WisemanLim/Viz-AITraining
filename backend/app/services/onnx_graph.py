"""Parse ONNX ModelProto into dashboard-friendly graph JSON."""
from __future__ import annotations

import uuid
from typing import Any

import onnx
from onnx import ModelProto


def _tensor_shape(value_info) -> list[str | int] | None:
    if not value_info.type.HasField("tensor_type"):
        return None
    tensor_type = value_info.type.tensor_type
    if not tensor_type.HasField("shape"):
        return None
    dims: list[str | int] = []
    for dim in tensor_type.shape.dim:
        if dim.HasField("dim_value"):
            dims.append(int(dim.dim_value))
        elif dim.HasField("dim_param"):
            dims.append(str(dim.dim_param))
        else:
            dims.append("?")
    return dims


def _value_info_map(graph) -> dict[str, list[str | int] | None]:
    shapes: dict[str, list[str | int] | None] = {}
    for vi in list(graph.input) + list(graph.output) + list(graph.value_info):
        shapes[vi.name] = _tensor_shape(vi)
    return shapes


def parse_onnx_bytes(data: bytes) -> dict[str, Any]:
    """Load ONNX from bytes and return nodes, edges, metadata."""
    model = onnx.load_model_from_string(data)
    return parse_onnx_model(model)


def parse_onnx_model(model: ModelProto) -> dict[str, Any]:
    graph = model.graph
    shapes = _value_info_map(graph)
    initializer_names = {init.name for init in graph.initializer}

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    tensor_producers: dict[str, str] = {}

    for inp in graph.input:
        if inp.name in initializer_names:
            continue
        node_id = f"input:{inp.name}"
        nodes.append(
            {
                "id": node_id,
                "label": inp.name,
                "op_type": "Input",
                "inputs": [],
                "outputs": [inp.name],
                "shape": shapes.get(inp.name),
            }
        )
        tensor_producers[inp.name] = node_id

    for idx, node in enumerate(graph.node):
        node_id = f"node:{idx}"
        label = node.name if node.name else f"{node.op_type}_{idx}"
        output_names = list(node.output)
        nodes.append(
            {
                "id": node_id,
                "label": label,
                "op_type": node.op_type,
                "inputs": list(node.input),
                "outputs": output_names,
                "shape": shapes.get(output_names[0]) if output_names else None,
            }
        )
        for out in output_names:
            tensor_producers[out] = node_id

    for out in graph.output:
        if out.name in tensor_producers:
            continue
        node_id = f"output:{out.name}"
        nodes.append(
            {
                "id": node_id,
                "label": out.name,
                "op_type": "Output",
                "inputs": [out.name],
                "outputs": [],
                "shape": shapes.get(out.name),
            }
        )

    edge_idx = 0
    node_by_id = {n["id"]: n for n in nodes}
    for node in nodes:
        if node["op_type"] in ("Input",):
            continue
        target_id = node["id"]
        for inp_name in node["inputs"]:
            if inp_name in initializer_names:
                continue
            source_id = tensor_producers.get(inp_name)
            if source_id and source_id != target_id:
                edges.append(
                    {
                        "id": f"edge:{edge_idx}",
                        "source": source_id,
                        "target": target_id,
                        "label": inp_name,
                    }
                )
                edge_idx += 1

    opset = model.opset_import[0].version if model.opset_import else None
    producer = model.producer_name or None

    return {
        "nodes": nodes,
        "edges": edges,
        "metadata": {
            "opset_version": opset,
            "producer": producer,
            "node_count": len([n for n in nodes if n["op_type"] not in ("Input", "Output")]),
            "graph_name": graph.name or "onnx_graph",
        },
    }


def validate_onnx_bytes(data: bytes) -> None:
    model = onnx.load_model_from_string(data)
    onnx.checker.check_model(model)
