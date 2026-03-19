"""Schemas for analytics dashboard specification."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AlertSchema(BaseModel):
    """A metric alert threshold and response action."""

    metric: str
    threshold: str
    action: str


class CadenceSchema(BaseModel):
    """Review cadence for metrics."""

    daily: list[str] = Field(default_factory=list)
    weekly: list[str] = Field(default_factory=list)
    monthly: list[str] = Field(default_factory=list)


class DashboardSpecSchema(BaseModel):
    """Analytics dashboard specification with KPIs and alerts."""

    north_star_metric: str = ""
    north_star_target: str = ""
    primary_kpis: list[str] = Field(default_factory=list)
    secondary_metrics: list[str] = Field(default_factory=list)
    tracking_requirements: list[str] = Field(default_factory=list)
    cadence: CadenceSchema = Field(default_factory=CadenceSchema)
    alerts: list[AlertSchema] = Field(default_factory=list)
