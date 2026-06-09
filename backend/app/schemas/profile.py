"""Pydantic schemas for training profiling (M1.3)."""
from datetime import datetime

from pydantic import BaseModel, Field


class ProfilePoint(BaseModel):
    epoch: int = Field(ge=0)
    phase: str = Field(min_length=1, max_length=64)
    step: int | None = None
    cpu_percent: float | None = Field(default=None, ge=0, le=100)
    gpu_percent: float | None = Field(default=None, ge=0, le=100)
    memory_mb: float | None = Field(default=None, ge=0)
    throughput: float | None = Field(default=None, ge=0)
    duration_ms: float | None = Field(default=None, ge=0)


class ProfileBatchCreate(BaseModel):
    events: list[ProfilePoint] = Field(min_length=1)


class ProfilePointRead(BaseModel):
    id: int
    epoch: int
    phase: str
    step: int | None
    cpu_percent: float | None
    gpu_percent: float | None
    memory_mb: float | None
    throughput: float | None
    duration_ms: float | None
    recorded_at: datetime

    model_config = {"from_attributes": True}


class ProfileList(BaseModel):
    items: list[ProfilePointRead]
    total: int


class TimelinePhaseSummary(BaseModel):
    phase: str
    avg_cpu_percent: float | None
    avg_gpu_percent: float | None
    avg_throughput: float | None
    total_duration_ms: float | None
    event_count: int


class EpochTimeline(BaseModel):
    epoch: int
    phases: list[TimelinePhaseSummary]
    bottleneck_phase: str | None


class ProfileTimelineReport(BaseModel):
    run_id: str
    epochs: list[EpochTimeline]
    total_events: int
