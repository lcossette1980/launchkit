"""Synthesizer step — assembles the final FullReportSchema.

This is the last step in the pipeline. It:
1. Generates the executive summary
2. Generates the dashboard spec
3. Aggregates website analysis scores
4. Assembles everything into the canonical FullReportSchema
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from gtm.agents.base import BaseAgent
from gtm.schemas.report import (
    AnalysisMetadataSchema,
    BrandInfoSchema,
    ExecutiveSummarySchema,
    FullReportSchema,
    MarketResearchSchema,
)
from gtm.schemas.analysis import PageAnalysisSchema, ScoresSchema, WebsiteAnalysisSchema
from gtm.schemas.competitor import CompetitorAnalysisSchema, CompetitorSchema
from gtm.schemas.copy_kit import CopyKitSchema
from gtm.schemas.dashboard import DashboardSpecSchema
from gtm.schemas.experiments import ExperimentsBacklogSchema
from gtm.schemas.strategy import GTMStrategySchema


class SynthesizerAgent(BaseAgent):
    name = "synthesizer"
    role = "orchestrator"

    async def run(self, state: dict) -> dict:
        config = state["config"]
        await self._report_progress(
            state.get("job_id", ""), 90, "Synthesizing final report"
        )

        # 1. Generate executive summary
        exec_summary = await self._generate_executive_summary(state)

        # 2. Generate dashboard spec
        dashboard = await self._generate_dashboard_spec(state)

        # 3. Aggregate website analysis
        website = self._aggregate_website_analysis(state.get("page_analyses", []))

        # 4. Assemble the canonical report
        report = FullReportSchema(
            brand_info=BrandInfoSchema(
                brand=config["brand"],
                url=config["site_url"],
                audience_primary=config.get("audience_primary", ""),
                audience_secondary=config.get("audience_secondary", ""),
                main_offers=config.get("main_offers", ""),
                usp_key=config.get("usp_key", ""),
                business_size=config.get("business_size", ""),
                monthly_budget=config.get("monthly_budget", ""),
            ),
            executive_summary=exec_summary,
            website_analysis=website,
            market_research=self._build_market_research(state.get("market_research", {})),
            competitor_analysis=self._build_competitor_analysis(
                state.get("competitor_analyses", [])
            ),
            gtm_strategy=self._safe_parse(state.get("gtm_strategy", {}), GTMStrategySchema),
            experiments=self._safe_parse(state.get("experiments", {}), ExperimentsBacklogSchema),
            copy_kit=self._safe_parse(state.get("copy_kit", {}), CopyKitSchema),
            dashboard=self._safe_parse(dashboard, DashboardSpecSchema),
            metadata=AnalysisMetadataSchema(
                job_id=state.get("job_id", ""),
                analysis_depth=config.get("analysis_depth", "comprehensive"),
                pages_crawled=len(state.get("pages_crawled", [])),
                competitors_analyzed=len(state.get("competitor_analyses", [])),
                completed_at=datetime.now(timezone.utc),
            ),
        )

        state["report"] = report.model_dump(by_alias=True)

        await self._report_progress(state.get("job_id", ""), 100, "Analysis complete")
        return state

    async def _generate_executive_summary(self, state: dict) -> ExecutiveSummarySchema:
        """Generate narrative executive summary."""
        config = state["config"]

        prompt = f"""Synthesize all analysis into an executive summary for {config['brand']}.
Return ONLY valid JSON:
{{
  "overview": "2-3 paragraph executive overview",
  "key_findings": ["finding 1", "finding 2", ...at least 5],
  "top_priorities": ["priority 1", "priority 2", ...at least 5]
}}

Consider resource constraints — business size: {config.get('business_size', 'Small Team')},
budget: {config.get('monthly_budget', '$500-$2000')}.
Focus on high-ROI, actionable priorities.

Website scores: {json.dumps([a.get('scores', {}) for a in state.get('page_analyses', [])[:3]], default=str)[:500]}
Strategy quick wins: {json.dumps(state.get('gtm_strategy', {}).get('quick_wins', []), default=str)[:500]}
Top experiments: {json.dumps([e.get('title', '') for e in state.get('experiments', {}).get('experiments', [])[:5]], default=str)[:300]}
"""

        data = await self._generate_json(
            prompt,
            required_keys=["overview", "key_findings", "top_priorities"],
            min_counts={"key_findings": 3, "top_priorities": 3},
            brand=config["brand"],
            audience=config["audience_primary"],
        )

        return ExecutiveSummarySchema(**data) if data else ExecutiveSummarySchema()

    async def _generate_dashboard_spec(self, state: dict) -> dict:
        """Generate the analytics dashboard specification."""
        config = state["config"]

        prompt = f"""Return ONLY valid JSON. Create a dashboard spec for {config['brand']}:
{{
  "north_star_metric": "the single most important metric",
  "north_star_target": "target value and timeframe",
  "primary_kpis": ["KPI 1", ...],
  "secondary_metrics": ["metric 1", ...],
  "tracking_requirements": ["requirement 1", ...],
  "cadence": {{ "daily": [...], "weekly": [...], "monthly": [...] }},
  "alerts": [{{"metric": "...", "threshold": "...", "action": "..."}}]
}}

Tie metrics to the actual funnel and audience: {config['audience_primary']}.
"""

        return await self._generate_json(
            prompt,
            required_keys=["north_star_metric", "primary_kpis", "alerts"],
            brand=config["brand"],
            audience=config["audience_primary"],
        )

    def _aggregate_website_analysis(
        self, page_analyses: list[dict]
    ) -> WebsiteAnalysisSchema:
        """Aggregate per-page analyses into overall website analysis."""
        pages = []
        all_strengths: list[str] = []
        all_weaknesses: list[str] = []
        all_recommendations: list[str] = []
        all_quick_wins: list[str] = []
        score_totals: dict[str, list[int]] = {
            "clarity": [], "audience_fit": [], "conversion": [], "seo": [], "ux": [],
        }

        for pa in page_analyses:
            pages.append(PageAnalysisSchema(
                url=pa.get("url", ""),
                title=pa.get("title", ""),
                strengths=pa.get("strengths", []),
                weaknesses=pa.get("weaknesses", []),
                recommendations=pa.get("recommendations", []),
                scores=ScoresSchema(**pa.get("scores", {})) if pa.get("scores") else ScoresSchema(),
                quick_wins=pa.get("quick_wins", []),
            ))
            all_strengths.extend(pa.get("strengths", []))
            all_weaknesses.extend(pa.get("weaknesses", []))
            all_recommendations.extend(pa.get("recommendations", []))
            all_quick_wins.extend(pa.get("quick_wins", []))

            scores = pa.get("scores", {})
            for key in score_totals:
                val = scores.get(key)
                if isinstance(val, (int, float)) and val > 0:
                    score_totals[key].append(int(val))

        # Average scores
        overall = ScoresSchema(**{
            k: int(sum(v) / len(v)) if v else 0
            for k, v in score_totals.items()
        })

        return WebsiteAnalysisSchema(
            pages_analyzed=pages,
            overall_scores=overall,
            top_strengths=all_strengths[:10],
            top_weaknesses=all_weaknesses[:10],
            top_recommendations=all_recommendations[:10],
            quick_wins=all_quick_wins[:10],
        )

    @staticmethod
    def _build_market_research(data: dict) -> MarketResearchSchema:
        return MarketResearchSchema(
            trends=data.get("trends", []),
            target_audience=data.get("target_audience", ""),
            competitive_landscape=data.get("competitive_landscape", ""),
            keyword_opportunities=data.get("keyword_opportunities", []),
            content_topics=data.get("content_topics", []),
        )

    @staticmethod
    def _build_competitor_analysis(analyses: list[dict]) -> CompetitorAnalysisSchema:
        competitors = []
        for a in analyses:
            competitors.append(CompetitorSchema(
                url=a.get("url", ""),
                name=a.get("name", ""),
                value_proposition=a.get("value_proposition", ""),
                target_audience=a.get("target_audience", ""),
                pricing_model=a.get("pricing_model", ""),
                key_differentiators=a.get("key_differentiators", []),
                strengths=a.get("strengths", []),
                weaknesses=a.get("weaknesses", []),
                content_strategy=a.get("content_strategy", ""),
            ))
        return CompetitorAnalysisSchema(competitors=competitors)

    @staticmethod
    def _safe_parse(data: dict, schema_cls: type):
        """Safely parse data into a schema, returning defaults on failure."""
        try:
            return schema_cls.model_validate(data)
        except Exception:
            return schema_cls()
