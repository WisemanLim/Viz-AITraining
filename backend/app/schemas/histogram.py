"""Histogram metric request/response schemas."""
import json

from pydantic import BaseModel, Field, field_validator


class HistogramPointCreate(BaseModel):
    tag: str = Field(..., min_length=1, max_length=255)
    bin_edges: list[float] = Field(..., min_length=2)
    counts: list[float] = Field(..., min_length=1)
    step: int | None = None

    @field_validator("counts")
    @classmethod
    def counts_match_bins(cls, v: list[float], info) -> list[float]:
        edges = info.data.get("bin_edges")
        if edges is not None and len(v) != len(edges) - 1:
            raise ValueError(
                f"counts length ({len(v)}) must equal bin_edges length - 1 ({len(edges) - 1})"
            )
        return v


class HistogramBatchCreate(BaseModel):
    histograms: list[HistogramPointCreate] = Field(..., min_length=1)


class HistogramPointRead(BaseModel):
    id: int
    run_id: str
    tag: str
    step: int | None
    bin_edges: list[float]
    counts: list[float]

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_row(cls, row) -> "HistogramPointRead":
        return cls(
            id=row.id,
            run_id=row.run_id,
            tag=row.tag,
            step=row.step,
            bin_edges=json.loads(row.bin_edges_json),
            counts=json.loads(row.counts_json),
        )


class HistogramList(BaseModel):
    items: list[HistogramPointRead]
    total: int
