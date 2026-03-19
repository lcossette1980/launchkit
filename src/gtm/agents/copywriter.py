"""Copy kit generation step — headlines, emails, social, ads."""

from __future__ import annotations

from gtm.agents.base import BaseAgent


class CopywriterAgent(BaseAgent):
    name = "copywriter"
    role = "writer"

    async def run(self, state: dict) -> dict:
        config = state["config"]
        await self._report_progress(
            state.get("job_id", ""), 82, "Creating copy and messaging kit"
        )

        prompt = f"""Return ONLY valid JSON. Create a complete copy kit for {config['brand']}:
{{
  "headlines": [
    {{"headline": "main headline", "subheadline": "supporting text", "cta": "button text"}},
    ...at least 5 variants
  ],
  "value_propositions": ["VP 1", "VP 2", "VP 3"],
  "emails": {{
    "welcome": {{"subject": "...", "body": "..."}},
    "follow_up": {{"subject": "...", "body": "..."}},
    "re_engagement": {{"subject": "...", "body": "..."}}
  }},
  "linkedin_messages": {{
    "connection_request": "message text",
    "follow_up": "message text",
    "value_share": "message text"
  }},
  "ads": {{
    "google_search": {{"headline": "...", "description": "...", "cta": "..."}},
    "facebook": {{"headline": "...", "description": "...", "cta": "..."}},
    "linkedin": {{"headline": "...", "description": "...", "cta": "..."}}
  }},
  "landing_page_sections": {{
    "problem": ["pain point 1", ...],
    "solution": ["how we solve it 1", ...],
    "benefits": ["benefit 1", ...],
    "social_proof": ["proof point 1", ...],
    "faq": ["Q: question? A: answer", ...]
  }}
}}

Brand: {config['brand']}
Audience: {config['audience_primary']}
USP: {config.get('usp_key', '')}
Main Offers: {config.get('main_offers', '')}

Write compelling, specific copy — not generic templates. Match the brand's voice.
Headlines should be A/B testable with clear value propositions.
"""

        copy_kit = await self._generate_json(
            prompt,
            required_keys=["headlines", "value_propositions", "landing_page_sections"],
            min_counts={"headlines": 3, "value_propositions": 3},
            brand=config["brand"],
            audience=config["audience_primary"],
        )

        state["copy_kit"] = copy_kit
        return state
