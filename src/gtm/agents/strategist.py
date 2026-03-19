"""GTM strategy generation step."""

from __future__ import annotations

import json

from gtm.agents.base import BaseAgent


class StrategistAgent(BaseAgent):
    name = "strategist"
    role = "orchestrator"

    async def run(self, state: dict) -> dict:
        config = state["config"]
        await self._report_progress(
            state.get("job_id", ""), 65, "Generating GTM strategy"
        )

        # Detect crawl failure
        page_analyses = state.get("page_analyses", [])
        crawl_failed = (
            not page_analyses
            or state.get("website_analysis", {}).get("crawl_failed")
        )

        if crawl_failed:
            website_context = (
                "Note: The website could not be crawled. Base your analysis on the "
                "provided brand information, target audience, market research, and "
                "competitor analysis instead of website content.\n\n"
                f"Brand: {config['brand']}\n"
                f"Main Offers: {config.get('main_offers', '')}\n"
                f"USP: {config.get('usp_key', '')}\n"
                f"Primary Audience: {config['audience_primary']}\n"
                f"Secondary Audience: {config.get('audience_secondary', '')}\n"
            )
        else:
            website_context = (
                "Website Analysis Summary (top findings):\n"
                f"{json.dumps(page_analyses[:3], indent=2, default=str)[:2500]}"
            )

        prompt = f"""Based on the analysis of {config['brand']}, return ONLY valid JSON:
{{
  "positioning": ["positioning statement 1", ...],
  "channels": {{ "primary": ["channel1", ...], "secondary": ["channel1", ...] }},
  "content_strategy": ["strategy point 1", ...],
  "partnerships": ["partnership opportunity 1", ...],
  "pricing": ["pricing recommendation 1", ...],
  "quick_wins": ["quick win 1", ...],
  "implementation_roadmap": {{
    "30_day": ["action 1", ...],
    "60_day": ["action 1", ...],
    "90_day": ["action 1", ...]
  }}
}}

Business Size: {config.get('business_size', 'Small Team')}
Budget: {config.get('monthly_budget', '$500-$2000')}
Audience: {config['audience_primary']}
USP: {config.get('usp_key', '')}
Main Offers: {config.get('main_offers', '')}

Be specific, actionable, and realistic for the budget. Include estimated costs where relevant.

{website_context}

Competitor Analysis Summary:
{json.dumps(state.get('competitor_analyses', [])[:3], indent=2, default=str)[:2500]}

Market Research:
{json.dumps(state.get('market_research', {}), indent=2, default=str)[:1500]}
"""

        strategy = await self._generate_json(
            prompt,
            required_keys=[
                "positioning", "channels", "content_strategy",
                "quick_wins", "implementation_roadmap",
            ],
            min_counts={"positioning": 2, "quick_wins": 3},
            brand=config["brand"],
            audience=config["audience_primary"],
        )

        state["gtm_strategy"] = strategy
        return state
