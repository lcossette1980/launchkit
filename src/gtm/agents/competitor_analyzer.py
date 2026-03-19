"""Competitor analysis step — crawls and analyzes competitor sites."""

from __future__ import annotations

import asyncio
import json

from gtm.agents.base import BaseAgent
from gtm.tools.web import WebTools


class CompetitorAnalyzerAgent(BaseAgent):
    name = "competitor_analyzer"
    role = "researcher"

    async def run(self, state: dict) -> dict:
        config = state["config"]
        competitor_urls = state.get("market_research", {}).get("competitor_urls", [])
        max_competitors = config.get("max_competitors", 5)

        await self._report_progress(
            state.get("job_id", ""), 50,
            f"Analyzing {min(len(competitor_urls), max_competitors)} competitors"
        )

        analyses: list[dict] = []
        web_tools = WebTools()
        await web_tools.initialize()

        try:
            for i, comp_url in enumerate(competitor_urls[:max_competitors]):
                pct = 50 + int((i / max(max_competitors, 1)) * 10)
                await self._report_progress(
                    state.get("job_id", ""), pct,
                    f"Analyzing competitor {i + 1}: {comp_url[:50]}"
                )

                analysis = await self._analyze_one(
                    web_tools, comp_url, config
                )
                analyses.append(analysis)
                await asyncio.sleep(2)  # Rate limiting
        finally:
            await web_tools.close()

        state["competitor_analyses"] = analyses
        self.logger.info("Analyzed %d competitors", len(analyses))
        return state

    async def _analyze_one(
        self, web_tools: WebTools, url: str, config: dict
    ) -> dict:
        """Crawl and analyze a single competitor."""
        try:
            data = await web_tools.browse(url, enable_interaction=False)

            if "error" in data:
                return self._error_result(url, data["error"])

            title = data.get("title", "")
            headings = data.get("structured_data", {}).get("headings", [])

            prompt = f"""Return ONLY valid JSON. Analyze this competitor:
{{
  "name": "",
  "value_proposition": "",
  "target_audience": "",
  "pricing_model": "",
  "key_differentiators": [],
  "strengths": [],
  "weaknesses": [],
  "content_strategy": ""
}}

URL: {url}
Title: {title}
Main Headings: {json.dumps(headings[:10], indent=2)}
Compare to our brand: {config['brand']}
Provide concrete, page-grounded observations. Be specific."""

            result = await self._generate_json(
                prompt,
                context={"title": title, "url": url, "headings": headings[:10]},
                required_keys=[
                    "value_proposition", "target_audience", "strengths", "weaknesses",
                ],
                brand=config["brand"],
                audience=config["audience_primary"],
            )

            result["url"] = url
            result.setdefault("name", title.split(" - ")[0].split(" | ")[0][:50])
            return result

        except Exception as e:
            self.logger.warning("Error analyzing competitor %s: %s", url, e)
            return self._error_result(url, str(e))

    @staticmethod
    def _error_result(url: str, error: str) -> dict:
        """Return a placeholder result for failed analyses."""
        domain = url.split("/")[2] if "://" in url else url
        return {
            "url": url,
            "name": domain,
            "value_proposition": f"Analysis failed for {domain}",
            "target_audience": "Could not determine",
            "pricing_model": "Information unavailable",
            "key_differentiators": [],
            "strengths": [],
            "weaknesses": [],
            "content_strategy": "Analysis incomplete",
            "error": error,
        }
