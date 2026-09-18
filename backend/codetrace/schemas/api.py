from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class VisualizeRequest(BaseModel):
    algorithm: str
    data: dict[str, Any] = Field(default_factory=dict)


class CompareRequest(BaseModel):
    algorithms: list[str] = Field(min_length=2, max_length=2)
    data: dict[str, Any] = Field(default_factory=dict)
    sizes: list[int] = Field(default_factory=lambda: [10, 50, 100, 200])


class EvaluateRequest(BaseModel):
    problem_id: str
    source: str = Field(min_length=1, max_length=200_000)


class HealthResponse(BaseModel):
    status: str
    version: str
    eval_enabled: bool
