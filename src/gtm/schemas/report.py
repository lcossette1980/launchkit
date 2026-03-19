"""FullReportSchema — THE single canonical output contract.

Every agent writes into this structure.
Every consumer (API, HTML report, JSON export) reads from it.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from gtm.schemas.analysis import WebsiteAnalysisSchema
from gtm.schemas.competitor import CompetitorAnalysisSchema
from gtm.schemas.copy_kit import CopyKitSchema
from gtm.schemas.dashboard import DashboardSpecSchema
from gtm.schemas.experiments import ExperimentsBacklogSchema
from gtm.schemas.strategy import GTMStrategySchema


class BrandInfoSchema(BaseModel):
    """Brand identity and context."""

    brand: str
    url: str
    audience_primary: str = ""
    audience_secondary: str = ""
    main_offers: str = ""
    usp_key: str = ""
    business_size: str = ""
    monthly_budget: str = ""


class ExecutiveSummarySchema(BaseModel):
    """Executive summary with key findings."""

    overview: str = ""
    key_findings: list[str] = Field(default_factory=list)
    top_priorities: list[str] = Field(default_factory=list)


class MarketResearchSchema(BaseModel):
    """Market research insights."""

    trends: list[str] = Field(default_factory=list)
    target_audience: str = ""
    competitive_landscape: str = ""
    keyword_opportunities: list[str] = Field(default_factory=list)
    content_topics: list[str] = Field(default_factory=list)


class AnalysisMetadataSchema(BaseModel):
    """Metadata about the analysis run."""

    job_id: str = ""
    analysis_depth: str = "comprehensive"
    pages_crawled: int = 0
    competitors_analyzed: int = 0
    completed_at: datetime | None = None


class FullReportSchema(BaseModel):
    """The complete output of an analysis job.

    This is the single source of truth that flows from agents → storage → API → reports.
    """

    brand_info: BrandInfoSchema = Field(default_factory=BrandInfoSchema)
    executive_summary: ExecutiveSummarySchema = Field(default_factory=ExecutiveSummarySchema)
    website_analysis: WebsiteAnalysisSchema = Field(default_factory=WebsiteAnalysisSchema)
    market_research: MarketResearchSchema = Field(default_factory=MarketResearchSchema)
    competitor_analysis: CompetitorAnalysisSchema = Field(
        default_factory=CompetitorAnalysisSchema
    )
    gtm_strategy: GTMStrategySchema = Field(default_factory=GTMStrategySchema)
    experiments: ExperimentsBacklogSchema = Field(default_factory=ExperimentsBacklogSchema)
    copy_kit: CopyKitSchema = Field(default_factory=CopyKitSchema)
    dashboard: DashboardSpecSchema = Field(default_factory=DashboardSpecSchema)
    metadata: AnalysisMetadataSchema = Field(default_factory=AnalysisMetadataSchema)
