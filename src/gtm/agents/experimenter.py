"""Experiments backlog generation step."""

from __future__ import annotations

import json

from gtm.agents.base import BaseAgent


class ExperimenterAgent(BaseAgent):
    name = "experimenter"
    role = "analyst"

    async def run(self, state: dict) -> dict:
        config = state["config"]
        await self._report_progress(
            state.get("job_id", ""), 75, "Designing growth experiments"
        )

        # Detect crawl failure
        page_analyses = state.get("page_analyses", [])
        crawl_failed = (
            not page_analyses
            or state.get("website_analysis", {}).get("crawl_failed")
        )

        if crawl_failed:
            findings_context = (
                "Note: The website could not be crawled. Design experiments based on "
                "the provided brand information, market research, competitor gaps, and "
                "strategy — not website content.\n\n"
                f"Brand: {config['brand']}\n"
                f"Main Offers: {config.get('main_offers', '')}\n"
                f"USP: {config.get('usp_key', '')}\n"
                f"Primary Audience: {config['audience_primary']}\n"
                f"Secondary Audience: {config.get('audience_secondary', '')}\n"
                f"Business Size: {config.get('business_size', '')}\n\n"
                f"Market Research:\n"
                f"{json.dumps(state.get('market_research', {}), indent=2, default=str)[:1500]}\n\n"
                f"Competitor Insights:\n"
                f"{json.dumps(state.get('competitor_analyses', [])[:3], indent=2, default=str)[:1000]}\n\n"
                f"Strategy Quick Wins:\n"
                f"{json.dumps(state.get('gtm_strategy', {}).get('quick_wins', []), indent=2, default=str)[:500]}"
            )
        else:
            findings_context = (
                f"Key findings to base experiments on:\n"
                f"{json.dumps(page_analyses[:2], indent=2, default=str)[:1500]}\n"
                f"{json.dumps(state.get('gtm_strategy', {}).get('quick_wins', []), indent=2, default=str)[:500]}"
            )

        prompt = f"""Return ONLY valid JSON. Create 15-20 growth experiments for {config['brand']}:
{{
  "experiments": [
    {{
      "title": "experiment name",
      "hypothesis": "If we do X, then Y will happen because Z",
      "metric": "primary success metric",
      "baseline": null,
      "target": null,
      "impact": 8,
      "confidence": 7,
      "effort": 3,
      "details": "implementation details and steps"
    }}
  ]
}}

Rules:
- impact, confidence, effort are 1-10 integers
- Cover: messaging, conversion, pricing, channels, content, SEO, partnerships
- Base experiments on actual findings from the analysis
- Be specific — reference actual pages, competitors, or opportunities found
- Prioritize experiments achievable within budget: {config.get('monthly_budget', '$500-$2000')}

{findings_context}
"""

        result = await self._generate_json(
            prompt,
            required_keys=["experiments"],
            min_counts={"experiments": 5},
            brand=config["brand"],
            audience=config["audience_primary"],
        )

        # Calculate and sort by ICE score
        for exp in result.get("experiments", []):
            impact = exp.get("impact", 5)
            confidence = exp.get("confidence", 5)
            effort = max(exp.get("effort", 5), 1)
            exp["ice_score"] = round((impact * confidence) / effort, 2)

        result["experiments"] = sorted(
            result.get("experiments", []),
            key=lambda x: x.get("ice_score", 0),
            reverse=True,
        )

        state["experiments"] = result
        self.logger.info(
            "Created %d experiments", len(result.get("experiments", []))
        )
        return state
