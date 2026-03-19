"""Schemas for GTM strategy."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChannelsSchema(BaseModel):
    """Marketing channel recommendations."""

    primary: list[str] = Field(default_factory=list)
    secondary: list[str] = Field(default_factory=list)


class RoadmapSchema(BaseModel):
    """30/60/90-day implementation roadmap.

    Uses field aliases so the LLM can return "30_day" keys and Pydantic
    maps them to valid Python attribute names.
    """

    day_30: list[str] = Field(default_factory=list, alias="30_day")
    day_60: list[str] = Field(default_factory=list, alias="60_day")
    day_90: list[str] = Field(default_factory=list, alias="90_day")

    model_config = {"populate_by_name": True}


class GTMStrategySchema(BaseModel):
    """Complete Go-To-Market strategy."""

    positioning: list[str] = Field(default_factory=list)
    channels: ChannelsSchema = Field(default_factory=ChannelsSchema)
    content_strategy: list[str] = Field(default_factory=list)
    partnerships: list[str] = Field(default_factory=list)
    pricing: list[str] = Field(default_factory=list)
    quick_wins: list[str] = Field(default_factory=list)
    implementation_roadmap: RoadmapSchema = Field(default_factory=RoadmapSchema)
