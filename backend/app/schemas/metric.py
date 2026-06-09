"""Pydantic schemas for metrics."""
from datetime import datetime

from pydantic import BaseModel, Field


class ScalarPoint(BaseModel):
    tag: str = Field(min_length=1, max_length=255)
    value: float
    step: int | None = None


class ScalarBatchCreate(BaseModel):
    metrics: list[ScalarPoint] = Field(min_length=1)


class ScalarPointRead(BaseModel):
    tag: str
    value: float
    step: int | None
    recorded_at: datetime

    model_config = {"from_attributes": True}


class ScalarList(BaseModel):
    items: list[ScalarPointRead]
    total: int
