"""ONNX graph request/response schemas."""
import json
from typing import Any

from pydantic import BaseModel, Field


class GraphNodeRead(BaseModel):
    id: str
    label: str
    op_type: str
    inputs: list[str]
    outputs: list[str]
    shape: list[str | int] | None = None


class GraphEdgeRead(BaseModel):
    id: str
    source: str
    target: str
    label: str | None = None


class GraphMetadataRead(BaseModel):
    opset_version: int | None = None
    producer: str | None = None
    node_count: int = 0
    graph_name: str = "onnx_graph"


class GraphRead(BaseModel):
    id: str
    run_id: str | None
    name: str
    nodes: list[GraphNodeRead]
    edges: list[GraphEdgeRead]
    metadata: GraphMetadataRead
    created_at: str

    model_config = {"from_attributes": True}


class GraphSummary(BaseModel):
    id: str
    run_id: str | None
    name: str
    node_count: int
    opset_version: int | None
    created_at: str


class GraphList(BaseModel):
    items: list[GraphSummary]
    total: int


def graph_from_row(row, parsed: dict[str, Any]) -> GraphRead:
    meta = parsed.get("metadata", {})
    return GraphRead(
        id=row.id,
        run_id=row.run_id,
        name=row.name,
        nodes=[GraphNodeRead.model_validate(n) for n in parsed.get("nodes", [])],
        edges=[GraphEdgeRead.model_validate(e) for e in parsed.get("edges", [])],
        metadata=GraphMetadataRead.model_validate(meta),
        created_at=row.created_at.isoformat(),
    )


def summary_from_row(row, parsed: dict[str, Any]) -> GraphSummary:
    meta = parsed.get("metadata", {})
    return GraphSummary(
        id=row.id,
        run_id=row.run_id,
        name=row.name,
        node_count=int(meta.get("node_count", 0)),
        opset_version=row.opset_version,
        created_at=row.created_at.isoformat(),
    )


def loads_graph_json(raw: str) -> dict[str, Any]:
    return json.loads(raw)
