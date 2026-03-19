"""Schemas for the experiments backlog."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ExperimentSchema(BaseModel):
    """A single growth experiment with ICE scoring."""

    title: str
    hypothesis: str = ""
    metric: str = ""
    baseline: float | None = None
    target: float | None = None
    impact: int = Field(default=5, ge=1, le=10)
    confidence: int = Field(default=5, ge=1, le=10)
    effort: int = Field(default=5, ge=1, le=10)
    ice_score: float = 0.0
    details: str = ""

    def compute_ice(self) -> float:
        """Calculate and set ICE score."""
        self.ice_score = (self.impact * self.confidence) / max(self.effort, 1)
        return self.ice_score


class ExperimentsBacklogSchema(BaseModel):
    """Collection of prioritized experiments."""

    experiments: list[ExperimentSchema] = Field(default_factory=list)

    def sort_by_ice(self) -> None:
        """Sort experiments descending by ICE score."""
        for exp in self.experiments:
            exp.compute_ice()
        self.experiments.sort(key=lambda e: e.ice_score, reverse=True)
