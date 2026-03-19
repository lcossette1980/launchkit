"""Request schemas for analysis configuration."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class AnalysisRequest(BaseModel):
    """Incoming request to start an analysis."""

    site_url: HttpUrl
    brand: str = Field(min_length=1, max_length=200)
    audience_primary: str = Field(min_length=1)
    audience_secondary: str = ""
    main_offers: str = ""
    geo_focus: str = "global"
    usp_key: str = ""

    business_size: Literal[
        "Solopreneur",
        "Small Team (2-10)",
        "Growing Business (11-50)",
        "Enterprise (50+)",
    ] = "Small Team (2-10)"
    monthly_budget: Literal[
        "< $500", "$500-$2000", "$2000-$5000", "$5000-$10000", "> $10000"
    ] = "$500-$2000"
    analysis_depth: Literal["quick", "standard", "comprehensive"] = "comprehensive"

    max_pages_to_scan: int = Field(default=50, ge=1, le=200)
    max_competitors: int = Field(default=5, ge=1, le=10)
    specific_competitors: list[str] = Field(default_factory=list)
    competitor_keywords: list[str] = Field(default_factory=list)
    exclude_competitors: list[str] = Field(default_factory=list)

    enable_interactive_scan: bool = True
