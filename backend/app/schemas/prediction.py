"""Response schemas for inference endpoints."""

from typing import Optional

from pydantic import BaseModel, Field


class Insight(BaseModel):
    feature: str = Field(..., description="Feature or metric name")
    detail: str = Field(..., description="Human-readable interpretation")
    level: str = Field(default="Info", description="Severity/importance label")


class PredictionResponse(BaseModel):
    status: str = Field(default="success")
    prediction: str = Field(..., description="Top predicted class")
    risk_score: Optional[float] = Field(default=None, description="0-100 confidence-derived score")
    all_probs: dict[str, float] = Field(..., description="Class probabilities for AD/HC/FTD")
    insights: list[Insight] = Field(default_factory=list)
