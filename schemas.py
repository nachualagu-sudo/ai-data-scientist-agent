from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class VisualizationRequest(BaseModel):
    chart_type: Literal["histogram", "bar", "scatter", "line", "box", "heatmap"]
    x_column: str | None = None
    y_column: str | None = None


class TrainRequest(BaseModel):
    target_column: str
    task_type: Literal["auto", "regression", "classification"] = "auto"
    model_type: Literal["auto", "linear", "logistic", "random_forest"] = "auto"
    test_size: float = Field(default=0.2, ge=0.1, le=0.4)


class PredictRequest(BaseModel):
    features: dict[str, Any]


class SalesFeatures(BaseModel):
    price: float = Field(gt=0)
    quantity: int = Field(gt=0)
    discount: float = Field(default=0, ge=0, le=100)
    month: int = Field(ge=1, le=12)
