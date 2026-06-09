"""XAI attribution schemas (M4)."""
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

XaiMethod = Literal["shap", "lime"]
XaiScope = Literal["local", "global", "temporal"]


class XaiAttributionCreate(BaseModel):
    method: XaiMethod
    scope: XaiScope
    step: int | None = None
    epoch: int | None = None
    title: str | None = None
    data: dict[str, Any]

    @model_validator(mode="after")
    def validate_payload(self) -> "XaiAttributionCreate":
        d = self.data
        if self.scope in ("local", "global"):
            if "features" not in d or "values" not in d:
                raise ValueError("local/global XAI requires features and values")
        elif self.scope == "temporal":
            if "steps" not in d or "features" not in d or "values_over_time" not in d:
                raise ValueError("temporal XAI requires steps, features, values_over_time")
        return self


class XaiBatchCreate(BaseModel):
    attributions: list[XaiAttributionCreate] = Field(min_length=1)


class XaiAttributionRead(BaseModel):
    id: int
    run_id: str
    method: XaiMethod
    scope: XaiScope
    step: int | None
    epoch: int | None
    title: str | None
    data: dict[str, Any]
    recorded_at: datetime

    model_config = {"from_attributes": True}


class XaiAttributionList(BaseModel):
    items: list[XaiAttributionRead]
    total: int
