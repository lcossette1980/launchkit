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
        crawl_errors = state.get("crawl_errors", [])
        website = self._aggregate_website_analysis(
            state.get("page_analyses", []),
            crawl_errors=crawl_errors,
        )

        # 4. Clean brand info — fix typos in user-provided text
        cleaned_brand = await self._clean_brand_info(config)

        # 5. Assemble the canonical report
        report = FullReportSchema(
            brand_info=BrandInfoSchema(
                brand=cleaned_brand.get("brand", config["brand"]),
                url=config["site_url"],
                audience_primary=cleaned_brand.get("audience_primary", config.get("audience_primary", "")),
                audience_secondary=cleaned_brand.get("audience_secondary", config.get("audience_secondary", "")),
                main_offers=cleaned_brand.get("main_offers", config.get("main_offers", "")),
                usp_key=cleaned_brand.get("usp_key", config.get("usp_key", "")),
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

    async def _clean_brand_info(self, config: dict) -> dict:
        """Fix typos and clean up user-provided brand info text."""
        fields_to_clean = {
            "brand": config.get("brand", ""),
            "audience_primary": config.get("audience_primary", ""),
            "audience_secondary": config.get("audience_secondary", ""),
            "main_offers": config.get("main_offers", ""),
            "usp_key": config.get("usp_key", ""),
        }

        # Only clean non-empty fields
        non_empty = {k: v for k, v in fields_to_clean.items() if v.strip()}
        if not non_empty:
            return fields_to_clean

        prompt = f"""Fix spelling and grammar errors in these brand info fields.
Return ONLY valid JSON with the corrected text. Do NOT change the meaning,
add new information, or rewrite — only fix typos and obvious misspellings.
If a field is already correct, return it unchanged.

{json.dumps(non_empty, indent=2)}"""

        try:
            cleaned = await self._generate_json(
                prompt,
                required_keys=list(non_empty.keys()),
                brand=config.get("brand", ""),
            )
            # Merge cleaned fields back, keeping originals for any missing keys
            result = dict(fields_to_clean)
            for k, v in cleaned.items():
                if k in result and isinstance(v, str) and v.strip():
                    result[k] = v
            return result
        except Exception:
            self.logger.warning("Brand info cleaning failed — using originals")
            return fields_to_clean

    async def _generate_executive_summary(self, state: dict) -> ExecutiveSummarySchema:
        """Generate narrative executive summary."""
        config = state["config"]
        page_analyses = state.get("page_analyses", [])
        crawl_errors = state.get("crawl_errors", [])

        # If zero pages were analyzed, produce a crawl-failure summary
        if not page_analyses:
            self.logger.warning(
                "No pages analyzed for %s — generating crawl-failure summary",
                config.get("site_url", "unknown"),
            )
            reasons = crawl_errors if crawl_errors else [
                "The site may be down or unreachable",
                "The site may block automated access (bot protection)",
                "The URL may be incorrect or misspelled",
                "The site may require authentication to access",
            ]
            overview = (
                f"We were unable to crawl the website at {config['site_url']}. "
                f"Our automated analysis could not retrieve any pages from this site. "
                f"Possible reasons: {'; '.join(reasons)}. "
                f"The remaining sections of this report (market research, competitor analysis, "
                f"strategy, etc.) are based on publicly available information and may still "
                f"be useful, but the website-specific scores and recommendations could not "
                f"be generated."
            )
            return ExecutiveSummarySchema(
                overview=overview,
                key_findings=[
                    f"Website at {config['site_url']} could not be crawled",
                    "Website scores are unavailable due to crawl failure",
                    "Review the URL for accuracy and ensure the site is publicly accessible",
                    "If the site uses bot protection (e.g., Cloudflare), manual review is recommended",
                    "Market research and competitor analysis are still available below",
                ],
                top_priorities=[
                    "Verify the website URL is correct and the site is live",
                    "Check if the site blocks automated access and consider whitelisting",
                    "Re-run the analysis once the site is accessible",
                    "Use the market research and competitor sections for immediate insights",
                    "Consider a manual website audit in the meantime",
                ],
            )

        prompt = f"""Synthesize all analysis into an executive summary for {config['brand']}.
Return ONLY valid JSON:
{{
  "biggest_problem": "The single biggest problem holding this business back right now (1-2 sentences)",
  "biggest_opportunity": "The single biggest untapped opportunity (1-2 sentences)",
  "best_next_move": "The #1 thing to do this week (1 sentence, specific and actionable)",
  "expected_impact": "What this move will achieve (1 sentence with a concrete outcome)",
  "top_3_actions": [
    "Action 1 for the next 14 days — specific, actionable, with expected result",
    "Action 2 for the next 14 days — specific, actionable, with expected result",
    "Action 3 for the next 14 days — specific, actionable, with expected result"
  ],
  "overview": "1-2 paragraph executive overview covering the full analysis",
  "key_findings": ["finding 1", "finding 2", ...5-7 max],
  "top_priorities": ["priority 1", "priority 2", ...3-5 max]
}}

CRITICAL RULES:
- The executive snapshot (biggest_problem, biggest_opportunity, best_next_move,
  expected_impact) should be sharp and opinionated. A founder should read these
  4 fields and immediately know what to do. No hedging.
- top_3_actions must be exactly 3. Not 5, not 10. Three.
- Each action must be completable within 14 days by a {config.get('business_size', 'Small Team')}
  with a {config.get('monthly_budget', '$500-$2000')} budget.
- top_priorities: 3-5 items max. Quality over quantity.
- key_findings: 5-7 items max. Each must cite specific data from the analysis.

Website scores: {json.dumps([a.get('scores', dict()) for a in page_analyses[:3]], default=str)[:500]}
Strategy quick wins: {json.dumps(state.get('gtm_strategy', dict()).get('quick_wins', []), default=str)[:500]}
Top experiments: {json.dumps([e.get('title', '') for e in state.get('experiments', dict()).get('experiments', [])[:5]], default=str)[:300]}
"""

        data = await self._generate_json(
            prompt,
            required_keys=["biggest_problem", "biggest_opportunity", "best_next_move", "top_3_actions", "overview"],
            min_counts={"top_3_actions": 3, "key_findings": 3},
            brand=config["brand"],
            audience=config["audience_primary"],
        )

        return ExecutiveSummarySchema(**data) if data else ExecutiveSummarySchema()

    async def _generate_dashboard_spec(self, state: dict) -> dict:
        """Generate the analytics dashboard specification."""
        config = state["config"]

        business_size = config.get("business_size", "Small Team")
        monthly_budget = config.get("monthly_budget", "")

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

Business size: {business_size}
Monthly budget: {monthly_budget}
Audience: {config['audience_primary']}

IMPORTANT GUIDELINES:
- Set REALISTIC targets grounded in the business size. A solopreneur with a $500-$2000
  budget is NOT going to hit 1000 paying customers in 12 months. Scale targets to what
  is achievable for a {business_size} with {monthly_budget} monthly budget.
- For solopreneurs: focus on early traction metrics (first 10-50 paying customers,
  first $1K-$5K MRR). For small teams: moderate growth (50-200 customers, $5K-$20K MRR).
  For established businesses: scaled targets are appropriate.
- Alert thresholds should be calibrated to the business stage — a solopreneur with
  3 customers doesn't need a "churn rate > 5%" alert.
- Tracking requirements should be practical tools a {business_size} can actually implement
  (e.g., suggest specific free/affordable analytics tools, not enterprise solutions).
"""

        return await self._generate_json(
            prompt,
            required_keys=["north_star_metric", "primary_kpis", "alerts"],
            brand=config["brand"],
            audience=config["audience_primary"],
        )

    def _aggregate_website_analysis(
        self, page_analyses: list[dict], *, crawl_errors: list[str] | None = None,
    ) -> WebsiteAnalysisSchema:
        """Aggregate per-page analyses into overall website analysis."""
        # Handle crawl failure: zero pages analyzed
        if not page_analyses:
            return WebsiteAnalysisSchema(
                pages_analyzed=[],
                overall_scores=None,
                crawl_failed=True,
                crawl_errors=crawl_errors or [],
            )

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
            top_strengths=all_strengths[:5],
            top_weaknesses=all_weaknesses[:5],
            top_recommendations=all_recommendations[:5],
            quick_wins=all_quick_wins[:5],
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

    def _safe_parse(self, data: dict, schema_cls: type):
        """Safely parse data into a schema, returning defaults on failure.

        On validation error, attempts to salvage partial data by stripping
        invalid items from lists (e.g., keep 14 valid experiments even if
        1 has an out-of-range score).
        """
        try:
            return schema_cls.model_validate(data)
        except Exception as e:
            self.logger.warning(
                "Schema validation failed for %s: %s — attempting partial salvage",
                schema_cls.__name__, str(e)[:200],
            )

        # Try to salvage list fields by validating items individually
        salvaged = {}
        for key, value in data.items():
            if isinstance(value, list):
                valid_items = []
                for item in value:
                    try:
                        # Try to find the item schema from the field annotation
                        field_info = schema_cls.model_fields.get(key)
                        if field_info and hasattr(field_info.annotation, '__args__'):
                            item_cls = field_info.annotation.__args__[0]
                            valid_items.append(item_cls.model_validate(item))
                        else:
                            valid_items.append(item)
                    except Exception:
                        self.logger.debug("Skipping invalid item in %s.%s", schema_cls.__name__, key)
                        continue
                salvaged[key] = valid_items
            else:
                salvaged[key] = value

        try:
            result = schema_cls.model_validate(salvaged)
            self.logger.info(
                "Salvaged %s with partial data",
                schema_cls.__name__,
            )
            return result
        except Exception:
            self.logger.error("Could not salvage %s — returning defaults", schema_cls.__name__)
            return schema_cls()
