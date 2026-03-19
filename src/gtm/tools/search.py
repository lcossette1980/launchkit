"""Search and research tools — SerpAPI, Ahrefs, SimilarWeb."""

from __future__ import annotations

import logging

import aiohttp

from gtm.config import Settings

logger = logging.getLogger(__name__)


class SearchTools:
    """Real search and research tools using external APIs."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def serp_search(self, query: str, *, num_results: int = 10) -> list[dict]:
        """Search using SerpAPI."""
        if not self.settings.serp_api_key:
            logger.warning("SERP API key not configured — returning empty results")
            return []

        params = {
            "q": query,
            "api_key": self.settings.serp_api_key,
            "num": num_results,
            "gl": "us",
        }

        session = await self._get_session()
        try:
            async with session.get("https://serpapi.com/search", params=params) as resp:
                data = await resp.json()
                return [
                    {
                        "title": r.get("title"),
                        "url": r.get("link"),
                        "snippet": r.get("snippet"),
                        "position": r.get("position"),
                    }
                    for r in data.get("organic_results", [])
                ]
        except Exception:
            logger.exception("SerpAPI search failed for query: %s", query)
            return []

    async def get_backlinks(self, domain: str) -> dict:
        """Get backlink data using Ahrefs API."""
        if not self.settings.ahrefs_api_key:
            return {}

        params = {
            "token": self.settings.ahrefs_api_key,
            "from": "backlinks",
            "target": domain,
            "mode": "domain",
            "limit": 100,
        }

        session = await self._get_session()
        try:
            async with session.get("https://apiv2.ahrefs.com", params=params) as resp:
                return await resp.json()
        except Exception:
            logger.exception("Ahrefs API failed for domain: %s", domain)
            return {}

    async def get_traffic_estimate(self, domain: str) -> dict:
        """Get traffic estimates using SimilarWeb API."""
        if not self.settings.similarweb_api_key:
            return {}

        url = (
            f"https://api.similarweb.com/v1/website/{domain}"
            f"/total-traffic-and-engagement/visits"
        )
        headers = {"api-key": self.settings.similarweb_api_key}

        session = await self._get_session()
        try:
            async with session.get(url, headers=headers) as resp:
                return await resp.json()
        except Exception:
            logger.exception("SimilarWeb API failed for domain: %s", domain)
            return {}
