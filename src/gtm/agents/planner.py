"""Plan analysis step — creates the analysis roadmap."""

from __future__ import annotations

from gtm.agents.base import BaseAgent


class PlannerAgent(BaseAgent):
    name = "planner"
    role = "orchestrator"

    async def run(self, state: dict) -> dict:
        config = state["config"]
        await self._report_progress(state.get("job_id", ""), 5, "Planning analysis approach")

        prompt = f"""
Plan a comprehensive website and GTM analysis for:
- Site: {config['site_url']}
- Brand: {config['brand']}
- Audience: {config['audience_primary']}
- Business Size: {config.get('business_size', 'Small Team')}
- Budget: {config.get('monthly_budget', '$500-$2000')}

Create a detailed analysis plan. Return ONLY valid JSON:
{{
    "pages_to_analyze": ["homepage", "about", "services", "pricing", "contact", "blog"],
    "competitor_queries": ["query1", "query2", ...],
    "key_metrics": ["metric1", "metric2", ...],
    "hypotheses": ["hypothesis1", ...],
    "content_needs": ["need1", ...]
}}

For pages_to_analyze, provide page TYPES not full URLs — we discover actual URLs by crawling.
"""

        plan = await self._generate_json(
            prompt,
            context={"brand": config["brand"], "audience": config["audience_primary"]},
            required_keys=["pages_to_analyze", "competitor_queries"],
            brand=config["brand"],
            audience=config["audience_primary"],
        )

        state["analysis_plan"] = plan
        self.logger.info(
            "Created analysis plan with %d page types",
            len(plan.get("pages_to_analyze", [])),
        )
        return state
