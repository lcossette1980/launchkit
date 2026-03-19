"""Schemas for website page analysis."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ScoresSchema(BaseModel):
    """Per-page quality scores (0-100)."""

    clarity: int = Field(default=0, ge=0, le=100)
    audience_fit: int = Field(default=0, ge=0, le=100)
    conversion: int = Field(default=0, ge=0, le=100)
    seo: int = Field(default=0, ge=0, le=100)
    ux: int = Field(default=0, ge=0, le=100)


class PageAnalysisSchema(BaseModel):
    """Analysis results for a single page."""

    url: str
    title: str = ""
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    scores: ScoresSchema = Field(default_factory=ScoresSchema)
    quick_wins: list[str] = Field(default_factory=list)


class WebsiteAnalysisSchema(BaseModel):
    """Aggregated website analysis across all pages."""

    pages_analyzed: list[PageAnalysisSchema] = Field(default_factory=list)
    overall_scores: ScoresSchema = Field(default_factory=ScoresSchema)
    top_strengths: list[str] = Field(default_factory=list)
    top_weaknesses: list[str] = Field(default_factory=list)
    top_recommendations: list[str] = Field(default_factory=list)
    quick_wins: list[str] = Field(default_factory=list)
