"""Market research step — discovers competitors and market insights."""

from __future__ import annotations

import re

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

IMPORTANT: Focus on DIRECT COMPETITORS — companies offering similar products/services
to a similar audience. Ignore results about health insurance, dictionaries, vocabulary
sites, or anything unrelated to {config.get('main_offers', 'the product category')}.

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
        """Run search queries and filter competitor URLs.

        Uses page analysis results (available from Step 3) to craft
        search queries grounded in what the site *actually* does,
        rather than relying on sparse user input or blind guesses.
        """
        import json

        brand = config["brand"]
        offers = config.get("main_offers", "")
        usp = config.get("usp_key", "")
        audience = config.get("audience_primary", "")
        site_url = config.get("site_url", "")

        negatives = (
            " -insurance -health -dictionary -vocabulary -definitions "
            "-g2 -cbinsights -trustradius -sourceforge -reddit -mdpi"
        )

        queries: list[str] = []

        # ── PRIMARY: LLM-generated queries from page analysis ──
        # By Step 4, we've already crawled and analyzed the site.
        # Use that understanding to craft precise competitor searches.
        page_analyses = state.get("page_analyses", [])
        if page_analyses:
            # Build a compact site summary for the LLM
            site_summary_parts = []
            for pa in page_analyses[:3]:
                title = pa.get("title", "")
                strengths = pa.get("strengths", [])[:2]
                if title:
                    site_summary_parts.append(f"Page: {title}")
                if strengths:
                    site_summary_parts.append(f"  Key features: {'; '.join(str(s)[:100] for s in strengths)}")
            site_summary = "\n".join(site_summary_parts)[:1200]

            query_prompt = f"""Based on this website analysis, generate 6 Google search queries
to find DIRECT COMPETITORS — companies offering similar products/services
to a similar audience.

Brand: {brand}
URL: {site_url}
Product: {offers}
USP: {usp}
Target audience: {audience}

Site analysis:
{site_summary}

Return ONLY valid JSON:
{{
  "queries": [
    "search query 1",
    "search query 2",
    "search query 3",
    "search query 4",
    "search query 5",
    "search query 6"
  ]
}}

RULES:
- Search for the PRODUCT CATEGORY, not the brand name
- Use terms like "alternatives to", "tools for", "software", "platform"
- Target the specific niche — not generic business tools
- Include audience-specific terms where relevant
- Do NOT include the brand name "{brand}" in queries
- Each query should find a DIFFERENT type of competitor"""

            try:
                result = await self._generate_json(
                    query_prompt,
                    required_keys=["queries"],
                    brand=brand,
                    audience=audience,
                )
                llm_queries = result.get("queries", [])
                # Append negatives to each LLM query
                for q in llm_queries[:6]:
                    if isinstance(q, str) and q.strip():
                        queries.append(f"{q}{negatives}")
                self.logger.info(
                    "Generated %d site-aware competitor queries", len(llm_queries)
                )
            except Exception:
                self.logger.warning("LLM query generation failed — falling back to config-based queries")

        # ── SECONDARY: Config-based queries (fallback / supplement) ──
        if len(queries) < 4:
            if offers:
                queries.append(f"{offers} SaaS tools software{negatives}")
                queries.append(f"best {offers} platforms for {audience}{negatives}")
            if usp:
                queries.append(f"{usp} software tools{negatives}")
            if audience and offers:
                queries.append(f"{audience} {offers} alternatives{negatives}")
            if brand:
                queries.append(f'"{brand}" competitors alternatives{negatives}')

            # Domain-word fallback when offers/usp are empty
            if not offers and not usp:
                domain_words = ""
                if site_url:
                    domain = site_url.split("//")[-1].split("/")[0].split(".")[0]
                    domain_words = " ".join(
                        w for w in re.split(r"[-_]|(?<=[a-z])(?=[A-Z])", domain)
                        if len(w) > 2
                    )
                if audience:
                    queries.append(f"tools for {audience}{negatives}")
                if domain_words:
                    queries.append(f"{domain_words} software alternatives{negatives}")

        # ── TERTIARY: Planner's pre-crawl queries (lowest priority) ──
        plan_queries = state.get("analysis_plan", {}).get("competitor_queries", [])
        for pq in plan_queries[:3]:
            if pq not in queries:
                queries.append(pq)

        # Deduplicate while preserving order
        seen_queries: set[str] = set()
        unique_queries: list[str] = []
        for q in queries:
            q_lower = q.lower().strip()
            if q_lower not in seen_queries:
                seen_queries.add(q_lower)
                unique_queries.append(q)

        all_urls: list[str] = []
        for query in unique_queries[:8]:
            results = await search_tools.serp_search(query)
            for r in results:
                url = r.get("url", "")
                if url and url != site_url:
                    all_urls.append(url)

        # Filter
        filtered = self._filter_competitor_urls(all_urls)

        return {
            "competitor_urls": filtered[:15],
            "market_queries": unique_queries[:8],
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
