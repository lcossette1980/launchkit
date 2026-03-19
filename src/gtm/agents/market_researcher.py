"""Market research step — discovers competitors and market insights."""

from __future__ import annotations

from gtm.agents.base import BaseAgent
from gtm.tools.search import SearchTools


# Domains to exclude from competitor results
EXCLUDED_DOMAINS = frozenset([
    "g2.com", "cbinsights.com", "trustradius.com", "reddit.com", "mdpi.com",
    "sourceforge.net", "wikipedia.org", "news.ycombinator.com", "forbes.com",
    "medium.com", "linkedin.com", "softwareworld.co", "softwaresuggest.com",
    "marketbeat.com", "aimagazine.com", "indeed.com", "glassdoor.com",
    "himalayas.app", "x.com", "twitter.com", "facebook.com", "instagram.com",
    "pinterest.com", "itqlick.com", "softwarefinder.com", "betterstack.com",
    "vault.com", "youtube.com", "tiktok.com",
])

EXCLUDED_PATH_FRAGMENTS = frozenset([
    "/post/", "/posts/", "/blog/", "/news/", "/article/",
    "/insights/", "/resources/",
])


class MarketResearcherAgent(BaseAgent):
    name = "market_researcher"
    role = "researcher"

    async def run(self, state: dict) -> dict:
        config = state["config"]
        await self._report_progress(
            state.get("job_id", ""), 40, "Researching market and competitors"
        )

        search_tools = SearchTools(self.settings)

        try:
            research_data = await self._research(config, state, search_tools)
        finally:
            await search_tools.close()

        # Analyze with LLM
        prompt = f"""Analyze the market research data for {config['brand']} in the {config.get('main_offers', '')} space.

Target audience: {config['audience_primary']}
USP: {config.get('usp_key', '')}

Based on search results and competitor landscape, return ONLY valid JSON:
{{
    "trends": ["trend1", ...],
    "target_audience": "detailed audience description",
    "competitive_landscape": "landscape summary",
    "keyword_opportunities": ["kw1", ...],
    "content_topics": ["topic1", ...]
}}
"""
        insights = await self._generate_json(
            prompt,
            context={"competitor_urls": research_data["competitor_urls"][:5]},
            required_keys=["trends", "competitive_landscape"],
            brand=config["brand"],
            audience=config["audience_primary"],
        )

        research_data.update(insights)
        state["market_research"] = research_data
        self.logger.info(
            "Found %d potential competitor URLs",
            len(research_data["competitor_urls"]),
        )
        return state

    async def _research(
        self, config: dict, state: dict, search_tools: SearchTools
    ) -> dict:
        """Run search queries and filter competitor URLs."""
        brand = config["brand"]
        offers = config.get("main_offers", "")

        # Build queries with brand disambiguation
        negatives = (
            ' -"Evolv AI" -EvolutionIQ -EvoluteIQ -weapons -security '
            "-g2 -cbinsights -trustradius -sourceforge -reddit -mdpi"
        )
        queries = [
            f'"{brand}" {offers} consulting training{negatives}',
            f"{offers} providers site:.com{negatives}",
            f'"{brand}" competitors{negatives}',
        ]
        # Add LLM-suggested queries
        plan_queries = state.get("analysis_plan", {}).get("competitor_queries", [])
        queries.extend(plan_queries[:5])

        all_urls: list[str] = []
        for query in queries[:8]:
            results = await search_tools.serp_search(query)
            for r in results:
                url = r.get("url", "")
                if url and url != config["site_url"]:
                    all_urls.append(url)

        # Filter
        filtered = self._filter_competitor_urls(all_urls)

        return {
            "competitor_urls": filtered[:10],
            "market_queries": queries,
        }

    @staticmethod
    def _filter_competitor_urls(urls: list[str]) -> list[str]:
        """Filter out noise — directories, news, social, academic."""
        seen: set[str] = set()
        filtered: list[str] = []

        for url in urls:
            url_lower = url.lower()
            domain = url_lower.split("/")[2] if "://" in url_lower else url_lower

            if any(d in domain for d in EXCLUDED_DOMAINS):
                continue
            if any(frag in url_lower for frag in EXCLUDED_PATH_FRAGMENTS):
                continue
            if url_lower.endswith(".pdf"):
                continue
            if domain in seen:
                continue

            seen.add(domain)
            filtered.append(url)

        return filtered
