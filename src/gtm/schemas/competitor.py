"""Schemas for competitor analysis."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CompetitorSchema(BaseModel):
    """Analysis of a single competitor."""

    url: str
    name: str = ""
    value_proposition: str = ""
    target_audience: str = ""
    pricing_model: str = ""
    key_differentiators: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    content_strategy: str = ""


class CompetitorAnalysisSchema(BaseModel):
    """Collection of competitor analyses."""

    competitors: list[CompetitorSchema] = Field(default_factory=list)
