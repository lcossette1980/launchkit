"""Sitemap discovery and parsing.

Discovers URLs from sitemap.xml, sitemap index files, and robots.txt.
"""

from __future__ import annotations

import logging

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


async def discover_from_sitemap(base_url: str, *, max_urls: int = 25) -> list[str]:
    """Discover page URLs from sitemap.xml, sitemap index, and robots.txt.

    Best-effort — failures are logged and silently skipped.
    """
    urls: list[str] = []
    domain = base_url.split("//")[-1].split("/")[0]
    candidates = [
        f"{base_url}/sitemap.xml",
        f"{base_url}/sitemap_index.xml",
        f"{base_url}/robots.txt",
    ]

    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for candidate in candidates:
            try:
                async with session.get(candidate) as resp:
                    if resp.status != 200:
                        continue
                    text = await resp.text()

                    if candidate.endswith("robots.txt"):
                        for line in text.splitlines():
                            if line.lower().startswith("sitemap:"):
                                sm_url = line.split(":", 1)[1].strip()
                                urls.extend(
                                    await _parse_sitemap(session, sm_url, domain)
                                )
                    else:
                        urls.extend(_parse_sitemap_content(text, domain))
            except Exception as e:
                logger.debug("Sitemap discovery error for %s: %s", candidate, e)

    # Deduplicate, preserve order, limit
    seen: set[str] = set()
    unique: list[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique.append(u)
    return unique[:max_urls]


async def _parse_sitemap(
    session: aiohttp.ClientSession, sitemap_url: str, domain: str
) -> list[str]:
    """Fetch and parse a single sitemap URL."""
    try:
        async with session.get(sitemap_url) as resp:
            if resp.status != 200:
                return []
            text = await resp.text()
            return _parse_sitemap_content(text, domain)
    except Exception as e:
        logger.debug("Failed to fetch sitemap %s: %s", sitemap_url, e)
        return []


def _parse_sitemap_content(xml_text: str, domain: str) -> list[str]:
    """Parse sitemap XML and extract page URLs (not sub-sitemaps)."""
    try:
        soup = BeautifulSoup(xml_text, "xml")
        urls: list[str] = []
        for loc in soup.find_all("loc"):
            link = loc.get_text(strip=True)
            if domain in link:
                urls.append(link)
        # Filter out sub-sitemap references
        return [u for u in urls if not u.endswith(".xml")]
    except Exception:
        return []
