"""Classical ML chart schemas (M1.4)."""
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

ChartType = Literal[
    "learning_curve", "roc", "confusion_matrix", "feature_importance"
]


class ClassicalChartCreate(BaseModel):
    chart_type: ChartType
    title: str | None = None
    data: dict[str, Any]

    @field_validator("data")
    @classmethod
    def validate_data(cls, v: dict[str, Any], info) -> dict[str, Any]:
        chart_type = info.data.get("chart_type")
        if chart_type == "learning_curve":
            for key in ("train_sizes", "train_scores", "val_scores"):
                if key not in v:
                    raise ValueError(f"learning_curve requires '{key}'")
        elif chart_type == "roc":
            for key in ("fpr", "tpr"):
                if key not in v:
                    raise ValueError(f"roc requires '{key}'")
        elif chart_type == "confusion_matrix":
            for key in ("labels", "matrix"):
                if key not in v:
                    raise ValueError(f"confusion_matrix requires '{key}'")
        elif chart_type == "feature_importance":
            for key in ("features", "importances"):
                if key not in v:
                    raise ValueError(f"feature_importance requires '{key}'")
        return v


class ClassicalBatchCreate(BaseModel):
    charts: list[ClassicalChartCreate] = Field(min_length=1)


class ClassicalChartRead(BaseModel):
    id: int
    run_id: str
    chart_type: ChartType
    title: str | None
    data: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class ClassicalChartList(BaseModel):
    items: list[ClassicalChartRead]
    total: int
