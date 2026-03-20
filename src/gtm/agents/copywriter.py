"""Copy kit generation step — headlines, emails, social, ads."""

from __future__ import annotations

import json

from gtm.agents.base import BaseAgent


class CopywriterAgent(BaseAgent):
    name = "copywriter"
    role = "writer"

    async def run(self, state: dict) -> dict:
        config = state["config"]
        await self._report_progress(
            state.get("job_id", ""), 82, "Creating copy and messaging kit"
        )

        # Detect crawl failure
        page_analyses = state.get("page_analyses", [])
        crawl_failed = (
            not page_analyses
            or state.get("website_analysis", {}).get("crawl_failed")
        )

        if crawl_failed:
            brand_context = (
                "Note: The website could not be crawled. Base your copy on the "
                "provided brand information, target audience, market research, and "
                "competitor analysis instead of website content.\n\n"
                f"Brand: {config['brand']}\n"
                f"Main Offers: {config.get('main_offers', '')}\n"
                f"USP: {config.get('usp_key', '')}\n"
                f"Primary Audience: {config['audience_primary']}\n"
                f"Secondary Audience: {config.get('audience_secondary', '')}\n"
                f"Business Size: {config.get('business_size', '')}\n\n"
                f"Market Research:\n"
                f"{json.dumps(state.get('market_research', {}), indent=2, default=str)[:1500]}\n\n"
                f"Competitor Insights:\n"
                f"{json.dumps(state.get('competitor_analyses', [])[:3], indent=2, default=str)[:1500]}\n"
            )
        else:
            brand_context = ""

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
    "social_proof": ["[DRAFT TEMPLATE] proof point 1", ...],
    "faq": ["Q: question? A: answer", ...]
  }}
}}

{brand_context}Brand: {config['brand']}
Audience: {config['audience_primary']}
USP: {config.get('usp_key', '')}
Main Offers: {config.get('main_offers', '')}
Business Size: {config.get('business_size', 'Small Team')}

VOICE & TONE GUIDELINES:
- Match copy to the audience's communication style. If the audience is developers
  or technical builders, write direct, specific, jargon-aware copy — no fluffy
  marketing speak. If the audience is non-technical, write clear and accessible copy.
- Avoid generic SaaS boilerplate. Every line should feel like it was written BY
  someone in the target audience FOR someone in the target audience.
- Use concrete numbers, outcomes, and specifics over vague promises.
- Headlines should be A/B testable with clear value propositions.
- Social proof items are DRAFT TEMPLATES for the user to customize with real customer
  quotes. Prefix each with "[DRAFT TEMPLATE]" so users know these are placeholders.
  Use realistic scenarios but make it clear these are examples to be replaced with
  actual testimonials. Use placeholder names like "[Customer Name]" not fake names.
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
