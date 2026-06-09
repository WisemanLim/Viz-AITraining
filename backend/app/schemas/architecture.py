"""Neural architecture visualization schemas."""
from pydantic import BaseModel


class ArchNode(BaseModel):
    id: str
    index: int
    activation: float
    hue: str


class ArchBias(BaseModel):
    value: float
    label: str


class ArchLayer(BaseModel):
    id: str
    name: str
    kind: str
    nodes: list[ArchNode]
    size: int
    bias: ArchBias


class ArchEdge(BaseModel):
    id: str
    source: str
    target: str
    weight: float
    label: str
    source_index: int
    target_index: int


class ArchConnection(BaseModel):
    id: str
    from_layer: int
    to_layer: int
    matrix: list[list[float]]
    shape: list[int]


class ArchFormula(BaseModel):
    id: str
    text: str
    x: float
    y: float


class ArchitectureView(BaseModel):
    graph_id: str
    source: str
    artifact_missing: bool
    layers: list[ArchLayer]
    edges: list[ArchEdge]
    connections: list[ArchConnection]
    formulas: list[ArchFormula]
