"""Internal training state schemas (M3.2–M3.5)."""
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

InternalKind = Literal["activation_map", "gradient_flow", "embedding", "hidden_state"]


class InternalMetricCreate(BaseModel):
    kind: InternalKind
    layer: str | None = None
    step: int | None = None
    epoch: int | None = None
    title: str | None = None
    data: dict[str, Any]

    @model_validator(mode="after")
    def validate_payload(self) -> "InternalMetricCreate":
        d = self.data
        if self.kind == "activation_map":
            if "width" not in d or "height" not in d or "values" not in d:
                raise ValueError("activation_map requires width, height, values")
        elif self.kind == "gradient_flow":
            if "timesteps" not in d or "layers" not in d or "magnitudes" not in d:
                raise ValueError("gradient_flow requires timesteps, layers, magnitudes")
        elif self.kind == "embedding":
            if "points" not in d:
                raise ValueError("embedding requires points")
        elif self.kind == "hidden_state":
            if "timesteps" not in d or "states" not in d:
                raise ValueError("hidden_state requires timesteps, states")
        return self


class InternalBatchCreate(BaseModel):
    metrics: list[InternalMetricCreate] = Field(min_length=1)


class InternalMetricRead(BaseModel):
    id: int
    run_id: str
    kind: InternalKind
    layer: str | None
    step: int | None
    epoch: int | None
    title: str | None
    data: dict[str, Any]
    recorded_at: datetime

    model_config = {"from_attributes": True}


class InternalMetricList(BaseModel):
    items: list[InternalMetricRead]
    total: int
