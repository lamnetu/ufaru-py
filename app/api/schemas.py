# app/api/schemas.py
from __future__ import annotations

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


class RewriteMode(str, Enum):
    rewrite = "rewrite"
    summary = "summary"
    social = "social"
    seo = "seo"
    official = "official"
    custom = "custom"


class RewriteRequest(BaseModel):
    text: Annotated[str, Field(min_length=10, max_length=20_000,
                               description="Исходный текст новости")]
    mode: RewriteMode = RewriteMode.rewrite
    custom_prompt: Annotated[str | None, Field(
        default=None, max_length=2000,
        description="Своя системная инструкция (только для mode=custom)"
    )] = None
    temperature: Annotated[float, Field(ge=0.0, le=1.5)] = 0.6
    max_tokens: Annotated[int, Field(ge=64, le=8192)] = 2048
    target_audience: Annotated[str | None, Field(max_length=200)] = None


class RewriteResponse(BaseModel):
    original: str
    result: str
    mode: RewriteMode
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    duration_ms: int
    cached: bool


class ErrorResponse(BaseModel):
    code: str
    message: str


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str
