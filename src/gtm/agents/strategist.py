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

Be specific, actionable, and realistic for the budget. Include estimated costs where relevant.

Website Analysis Summary (top findings):
{json.dumps(state.get('page_analyses', [])[:3], indent=2, default=str)[:2500]}

Competitor Analysis Summary:
{json.dumps(state.get('competitor_analyses', [])[:3], indent=2, default=str)[:2500]}
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
