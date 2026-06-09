"""Pydantic schemas for runs."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RunCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    params: dict[str, Any] | None = None


class RunRead(BaseModel):
    id: str
    name: str
    status: str
    params: dict[str, Any] | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RunList(BaseModel):
    items: list[RunRead]
    total: int
