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
        max_competitors = config.get("max_competitors", 8)

        await self._report_progress(
            state.get("job_id", ""), 50,
            f"Analyzing {min(len(competitor_urls), max_competitors)} competitors"
        )

        raw_analyses: list[dict] = []
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
                raw_analyses.append(analysis)
                await asyncio.sleep(2)  # Rate limiting
        finally:
            await web_tools.close()

        # Filter out failed crawls and irrelevant competitors
        analyses = self._filter_valid_analyses(raw_analyses, config)

        state["competitor_analyses"] = analyses
        self.logger.info(
            "Analyzed %d competitors (%d filtered out of %d raw)",
            len(analyses), len(raw_analyses) - len(analyses), len(raw_analyses),
        )
        return state

    async def _analyze_one(
        self, web_tools: WebTools, url: str, config: dict
    ) -> dict:
        """Crawl and analyze a single competitor (homepage + pricing/features)."""
        try:
            data = await web_tools.browse(url, enable_interaction=False)

            if "error" in data:
                return self._error_result(url, data["error"])

            title = data.get("title", "")
            headings = data.get("structured_data", {}).get("headings", [])

            # Detect security/bot-protection pages that return no useful content
            title_lower = title.lower()
            if any(indicator in title_lower for indicator in [
                "security", "captcha", "verify", "challenge",
                "access denied", "forbidden", "cloudflare",
                "just a moment", "checking your browser",
            ]):
                return self._error_result(url, f"Security/bot protection page: {title}")

            if not headings and len(title) < 5:
                return self._error_result(url, "Page returned no meaningful content")

            # Deep crawl: find and crawl pricing + features pages
            extra_pages_content = await self._crawl_key_pages(web_tools, data, url)

            prompt = f"""Return ONLY valid JSON. Analyze this competitor:
{{
  "name": "",
  "value_proposition": "",
  "target_audience": "",
  "pricing_model": "",
  "key_differentiators": [],
  "strengths": [],
  "weaknesses": [],
  "content_strategy": "",
  "relevance_score": 0
}}

URL: {url}
Title: {title}
Main Headings: {json.dumps(headings[:10], indent=2)}
{extra_pages_content}

Our brand: {config['brand']}
Our audience: {config['audience_primary']}
Our offers: {config.get('main_offers', 'N/A')}

IMPORTANT: Set "relevance_score" from 1-10 indicating how relevant this competitor is
to our brand. A direct competitor offering similar products to a similar audience = 8-10.
A tangentially related company = 4-7. A completely unrelated company = 1-3.

If this page appears to be a security checkpoint, error page, or irrelevant site
(e.g., a church platform when analyzing a dev tool), set relevance_score to 1.

Provide concrete, page-grounded observations. Be specific.
If pricing page data is available, extract ACTUAL pricing tiers and amounts."""

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

    async def _crawl_key_pages(
        self, web_tools: WebTools, homepage_data: dict, base_url: str
    ) -> str:
        """Find and crawl pricing/features pages from competitor homepage links."""
        links = homepage_data.get("structured_data", {}).get("links", [])
        if not links:
            return ""

        # Extract base domain for filtering
        from urllib.parse import urlparse
        parsed = urlparse(base_url)
        domain = parsed.netloc

        # Find pricing and features page URLs
        target_patterns = {
            "pricing": ["pricing", "plans", "price", "packages"],
            "features": ["features", "product", "solutions", "platform", "how-it-works"],
        }
        found_urls: dict[str, str] = {}

        for link in links:
            if not isinstance(link, dict):
                continue
            href = link.get("href", "")
            text = (link.get("text") or "").lower()
            if not href or link.get("external", False):
                continue
            # Normalize URL
            if href.startswith("/"):
                href = f"{parsed.scheme}://{domain}{href}"
            elif not href.startswith("http"):
                continue
            # Check if URL matches any target pattern
            href_lower = href.lower()
            for page_type, patterns in target_patterns.items():
                if page_type in found_urls:
                    continue
                if any(p in href_lower or p in text for p in patterns):
                    found_urls[page_type] = href
                    break

        if not found_urls:
            return ""

        # Crawl found pages (max 2)
        extra_content_parts = []
        for page_type, page_url in list(found_urls.items())[:2]:
            try:
                page_data = await web_tools.browse(page_url, enable_interaction=False)
                if page_data and "error" not in page_data:
                    page_headings = page_data.get("structured_data", {}).get("headings", [])
                    # Extract text
                    from bs4 import BeautifulSoup
                    import re
                    text = BeautifulSoup(
                        page_data.get("content", ""), "html.parser"
                    ).get_text(separator=" ")
                    text = re.sub(r"\s+", " ", text)[:1500]
                    extra_content_parts.append(
                        f"\n--- {page_type.upper()} PAGE ({page_url}) ---\n"
                        f"Title: {page_data.get('title', '')}\n"
                        f"Headings: {json.dumps(page_headings[:8])}\n"
                        f"Content: {text}"
                    )
                await asyncio.sleep(1)
            except Exception as e:
                self.logger.debug("Failed to crawl %s page %s: %s", page_type, page_url, e)

        return "\n".join(extra_content_parts) if extra_content_parts else ""

    def _filter_valid_analyses(
        self, analyses: list[dict], config: dict
    ) -> list[dict]:
        """Filter out failed crawls and irrelevant competitors."""
        valid = []
        for a in analyses:
            # Skip entries that had crawl errors
            if a.get("error"):
                self.logger.info(
                    "Filtering out %s: crawl error — %s",
                    a.get("url", "unknown"), a.get("error", "")[:80],
                )
                continue

            # Skip entries with low relevance scores
            relevance = a.get("relevance_score", 5)
            try:
                relevance = int(relevance)
            except (TypeError, ValueError):
                relevance = 5

            if relevance < 4:
                self.logger.info(
                    "Filtering out %s: low relevance score %d",
                    a.get("url", "unknown"), relevance,
                )
                continue

            # Skip entries with empty/generic value propositions
            vp = a.get("value_proposition", "")
            if not vp or "analysis failed" in vp.lower() or "could not" in vp.lower():
                self.logger.info(
                    "Filtering out %s: empty or failed value proposition",
                    a.get("url", "unknown"),
                )
                continue

            valid.append(a)

        return valid

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
