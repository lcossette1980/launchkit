"""Schemas for the experiments backlog."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class ExperimentSchema(BaseModel):
    """A single growth experiment with ICE scoring."""

    model_config = {"coerce_numbers_to_str": False}

    title: str
    hypothesis: str = ""
    metric: str = ""
    baseline: str | float | None = None  # LLMs often return strings like "current CTR: 2%"
    target: str | float | None = None  # LLMs often return strings like "increase by 25%"
    impact: int = Field(default=5)
    confidence: int = Field(default=5)
    effort: int = Field(default=5)
    ice_score: float = 0.0
    details: str = ""

    @field_validator("impact", "confidence", "effort", mode="before")
    @classmethod
    def clamp_score(cls, v):
        """Clamp to 1-10 instead of rejecting out-of-range values."""
        try:
            v = int(v)
        except (TypeError, ValueError):
            return 5
        return max(1, min(10, v))

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
