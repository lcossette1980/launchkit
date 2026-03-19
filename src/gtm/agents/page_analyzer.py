"""Page analysis step — deep analysis of each crawled page."""

from __future__ import annotations

import json
import re

from bs4 import BeautifulSoup

from gtm.agents.base import BaseAgent


class PageAnalyzerAgent(BaseAgent):
    name = "page_analyzer"
    role = "analyst"

    async def run(self, state: dict) -> dict:
        config = state["config"]
        pages = state.get("pages_crawled", [])
        analyses: list[dict] = []

        for i, page in enumerate(pages):
            if "error" in page:
                continue

            pct = 25 + int((i / max(len(pages), 1)) * 15)
            await self._report_progress(
                state.get("job_id", ""), pct,
                f"Analyzing page {i + 1} of {len(pages)}: {page.get('title', '')[:40]}"
            )

            # Extract visible text for context
            try:
                text_sample = BeautifulSoup(
                    page.get("content", ""), "html.parser"
                ).get_text(separator="\n")
                text_sample = re.sub(r"\s+", " ", text_sample)[:1500]
            except Exception:
                text_sample = ""

            perf = page.get("metrics", {})

            prompt = f"""Analyze this webpage and return ONLY valid JSON matching this schema:
{{
  "strengths": ["specific strength 1", ...],
  "weaknesses": ["specific weakness 1", ...],
  "recommendations": ["actionable recommendation 1", ...],
  "scores": {{ "clarity": 0, "audience_fit": 0, "conversion": 0, "seo": 0, "ux": 0 }},
  "quick_wins": ["quick win 1", ...]
}}

Rules:
- Provide SPECIFIC, evidence-based items grounded in the actual content below.
- Scores must be integers 0-100.
- At least 3 items per list.
- Reference actual page elements (headings, CTAs, forms, copy) in your observations.

Page URL: {page['url']}
Title: {page.get('title', '')}
Performance (ms): loadTime={perf.get('loadTime', 'n/a')} domReady={perf.get('domReady', 'n/a')} firstPaint={perf.get('firstPaint', 'n/a')}
Structured Data (truncated):
{json.dumps(page.get('structured_data', {}), indent=2)[:1000]}
Visible Text (truncated):
{text_sample}"""

            analysis = await self._generate_json(
                prompt,
                required_keys=["strengths", "weaknesses", "recommendations", "scores"],
                min_counts={"strengths": 2, "weaknesses": 2, "recommendations": 2},
                brand=config["brand"],
                audience=config["audience_primary"],
            )

            analyses.append({
                "url": page["url"],
                "title": page.get("title", ""),
                "strengths": analysis.get("strengths", []),
                "weaknesses": analysis.get("weaknesses", []),
                "recommendations": analysis.get("recommendations", []),
                "scores": analysis.get("scores", {}),
                "quick_wins": analysis.get("quick_wins", []),
            })

        state["page_analyses"] = analyses
        self.logger.info("Analyzed %d pages", len(analyses))
        return state
