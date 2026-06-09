"""Multi-run comparison schemas."""
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.metric import ScalarPointRead
from app.schemas.run import RunRead


class ParamDiff(BaseModel):
    key: str
    values: dict[str, Any]


class SeriesByRun(BaseModel):
    run_id: str
    run_name: str
    points: list[ScalarPointRead]


class TagSeries(BaseModel):
    tag: str
    series: list[SeriesByRun]


class CompareResult(BaseModel):
    runs: list[RunRead]
    param_diffs: list[ParamDiff]
    tags: list[TagSeries]


class CompareRequest(BaseModel):
    run_ids: list[str] = Field(..., min_length=2, max_length=8)
