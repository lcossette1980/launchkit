"""Website crawling step — discovers and crawls pages.

Preserves the sophisticated page discovery logic from the original system:
- Homepage crawl with link extraction
- Priority scoring (nav links, heading tokens, important patterns)
- Sitemap discovery
- Fallback paths
"""

from __future__ import annotations

import asyncio
import re

from gtm.agents.base import BaseAgent
from gtm.tools.sitemap import discover_from_sitemap
from gtm.tools.web import WebTools


class CrawlerAgent(BaseAgent):
    name = "crawler"
    role = "orchestrator"

    async def run(self, state: dict) -> dict:
        config = state["config"]
        base_url = config["site_url"].rstrip("/")

        await self._report_progress(state.get("job_id", ""), 10, f"Crawling {base_url}")

        web_tools = WebTools()
        await web_tools.initialize()

        pages_data: list[dict] = []
        crawl_errors: list[str] = []

        try:
            # 1. Crawl homepage (with desktop + mobile screenshots)
            self.logger.info("Discovering pages from %s", base_url)
            homepage = await web_tools.browse(base_url, capture_screenshot=True)
            if homepage and "error" not in homepage:
                # Also capture mobile screenshot for responsive analysis
                mobile_shot = await web_tools.mobile_screenshot(base_url)
                if mobile_shot:
                    homepage["mobile_screenshot"] = mobile_shot
                pages_data.append(homepage)
            elif homepage and "error" in homepage:
                error_msg = homepage["error"]
                self.logger.warning(
                    "Failed to crawl homepage %s: %s", base_url, error_msg
                )
                crawl_errors.append(self._classify_error(error_msg, base_url))

            # 2. Extract internal links with priority scoring
            discovered_urls = set([base_url])
            if homepage and "structured_data" in homepage:
                discovered_urls.update(
                    self._score_and_collect_urls(homepage, base_url)
                )

            # 3. Sitemap discovery
            sitemap_urls = await discover_from_sitemap(base_url)
            discovered_urls.update(sitemap_urls)

            self.logger.info(
                "Discovered %d internal pages (incl. sitemap)", len(discovered_urls)
            )

            # 4. Match LLM-suggested page types to discovered URLs
            suggested = state.get("analysis_plan", {}).get("pages_to_analyze", [])
            priority_urls = self._match_suggestions(suggested, discovered_urls)

            # 5. Add fallback paths if discovery was thin
            fallback_paths = [
                "/about", "/services", "/solutions", "/pricing", "/contact",
                "/blog", "/resources", "/case-studies", "/training",
                "/consulting", "/products", "/features", "/demo",
            ]
            fallback_urls = [f"{base_url}{p}" for p in fallback_paths]

            all_urls = list(priority_urls) + [
                u for u in discovered_urls if u not in priority_urls and u != base_url
            ]
            if len(all_urls) < 5:
                for u in fallback_urls:
                    if u not in all_urls:
                        all_urls.append(u)

            # 6. Crawl pages
            unique_urls = list(dict.fromkeys(all_urls))
            max_pages = max(1, config.get("max_pages_to_scan", 50) - 1)
            to_crawl = [u for u in unique_urls if u != base_url][:max_pages]

            for i, url in enumerate(to_crawl):
                pct = 10 + int((i / max(len(to_crawl), 1)) * 15)
                await self._report_progress(
                    state.get("job_id", ""), pct,
                    f"Crawling page {i + 1} of {len(to_crawl)}"
                )

                try:
                    # Capture screenshots for key pages (first 4)
                    take_screenshot = i < 4
                    page_data = await web_tools.browse(
                        url, capture_screenshot=take_screenshot
                    )
                    if page_data and "error" not in page_data:
                        pages_data.append(page_data)
                except Exception as e:
                    self.logger.warning("Error crawling %s: %s", url, e)

                await asyncio.sleep(1)  # Rate limiting

        finally:
            await web_tools.close()

        # Deduplicate pages with identical content (SPA shells, error pages)
        pages_data, crawl_warnings = self._deduplicate_pages(pages_data)

        # Check for broken internal links
        broken_links = await self._check_broken_links(pages_data, base_url)

        state["pages_crawled"] = pages_data
        state["crawl_errors"] = crawl_errors
        state["crawl_warnings"] = crawl_warnings
        state["broken_links"] = broken_links

        if not pages_data:
            self.logger.warning(
                "Crawl finished with ZERO pages for %s. Errors: %s",
                base_url,
                crawl_errors or ["No pages returned and no explicit errors captured"],
            )

        self.logger.info("Crawled %d pages (after dedup)", len(pages_data))
        return state

    def _score_and_collect_urls(self, homepage: dict, base_url: str) -> set[str]:
        """Score and collect internal URLs from homepage links."""
        urls: set[str] = set()
        structured = homepage.get("structured_data", {})
        links = structured.get("links", [])

        # Build priority tokens from headings
        headings = structured.get("headings", [])
        heading_text = " ".join(h.get("text", "") for h in headings)
        tokens = set(re.findall(r"[a-zA-Z][a-zA-Z\-]{3,20}", heading_text.lower()))

        important_patterns = [
            "about", "services", "solutions", "products", "pricing",
            "contact", "blog", "resources", "why-", "how-", "what-",
            "case-", "testimonial", "faq", "demo", "ai", "training",
        ]
        generic_types = {
            "about", "services", "solutions", "pricing", "contact",
            "blog", "programs", "offerings",
        }

        candidates: list[tuple[int, str]] = []
        for link in links:
            if not isinstance(link, dict):
                continue
            href = link.get("href", "")
            text = (link.get("text") or "").lower()
            is_nav = link.get("is_navigation", False)
            is_footer = link.get("is_footer", False)

            if not href or link.get("external", False):
                continue

            # Normalize
            if href.startswith("http"):
                if base_url not in href:
                    continue
                norm = href
            elif href.startswith("/"):
                norm = f"{base_url}{href}"
            else:
                continue

            # Score
            score = 0
            path_lower = norm.lower()
            if is_nav:
                score += 5
            if is_footer:
                score += 3
            for pattern in important_patterns:
                if pattern in path_lower:
                    score += 4
                    break
            for tok in tokens:
                if tok in path_lower:
                    score += 2
                    break
            if any(g in path_lower for g in generic_types):
                score += 2
            if any(t in text for t in tokens):
                score += 1

            candidates.append((score, norm.rstrip("/")))

        for _, url in sorted(candidates, key=lambda x: x[0], reverse=True)[:150]:
            urls.add(url)

        return urls

    @staticmethod
    def _match_suggestions(
        suggestions: list[str], discovered: set[str]
    ) -> list[str]:
        """Match LLM page type suggestions to discovered URLs."""
        matched: list[str] = []
        for suggestion in suggestions:
            slug = str(suggestion).lower().replace("/", "").replace("-", "")
            for url in discovered:
                if slug in url.lower().replace("/", "").replace("-", ""):
                    matched.append(url)
                    break
        return matched

    def _deduplicate_pages(
        self, pages: list[dict]
    ) -> tuple[list[dict], list[str]]:
        """Collapse pages with identical titles/content into a single entry.

        Returns the deduplicated page list and a list of warning messages.
        This catches SPAs that serve the same shell for every route and
        sites that return the same error page for non-existent URLs.
        """
        if len(pages) <= 1:
            return pages, []

        # Group pages by title (normalized)
        from collections import defaultdict

        title_groups: dict[str, list[dict]] = defaultdict(list)
        for page in pages:
            title = (page.get("title") or "").strip()
            title_groups[title].append(page)

        deduped: list[dict] = []
        warnings: list[str] = []

        for title, group in title_groups.items():
            if len(group) <= 2:
                # Small group — keep all pages
                deduped.extend(group)
                continue

            # More than 2 pages share the same title — likely duplicates
            is_error = any(
                kw in title.lower()
                for kw in ("404", "not found", "error", "page not found")
            )

            representative = group[0]
            duplicate_count = len(group) - 1
            representative["duplicate_count"] = duplicate_count
            representative["duplicate_urls"] = [
                p.get("url", "") for p in group[1:]
            ]
            deduped.append(representative)

            display_title = title if title else "(empty title)"
            if is_error:
                warnings.append(
                    f"{len(group)} pages returned '{display_title}' — "
                    f"the site may not serve unique content for each URL"
                )
                representative["is_error_page"] = True
            else:
                warnings.append(
                    f"{len(group)} pages returned identical title "
                    f"'{display_title}' — possible SPA without "
                    f"server-side rendering"
                )

            self.logger.info(
                "Collapsed %d duplicate pages with title '%s' into 1",
                len(group),
                display_title,
            )

        if warnings:
            self.logger.warning(
                "Crawl dedup warnings: %s", "; ".join(warnings)
            )

        return deduped, warnings

    async def _check_broken_links(
        self, pages: list[dict], base_url: str
    ) -> list[dict]:
        """Check internal links for 404s and broken resources."""
        import aiohttp

        # Collect unique internal links from all crawled pages
        internal_links: dict[str, str] = {}  # url -> source_page
        for page in pages:
            source = page.get("url", "")
            links = page.get("structured_data", {}).get("links", [])
            for link in links:
                if not isinstance(link, dict):
                    continue
                href = link.get("href", "")
                if not href or link.get("external", False):
                    continue
                if href.startswith("/"):
                    href = f"{base_url}{href}"
                if base_url in href and href not in internal_links:
                    internal_links[href] = source

        if not internal_links:
            return []

        # Check up to 30 links with HEAD requests
        broken: list[dict] = []
        urls_to_check = list(internal_links.items())[:30]

        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                for link_url, source_page in urls_to_check:
                    try:
                        async with session.head(
                            link_url, allow_redirects=True
                        ) as resp:
                            if resp.status >= 400:
                                broken.append({
                                    "url": link_url,
                                    "status": resp.status,
                                    "source_page": source_page,
                                })
                    except Exception:
                        broken.append({
                            "url": link_url,
                            "status": 0,
                            "source_page": source_page,
                            "error": "Connection failed",
                        })
        except Exception as e:
            self.logger.warning("Broken link check failed: %s", e)

        if broken:
            self.logger.info("Found %d broken links", len(broken))

        return broken

    @staticmethod
    def _classify_error(error_msg: str, url: str) -> str:
        """Classify a crawl error into a human-readable reason."""
        err = error_msg.lower()
        if "timeout" in err or "timedout" in err:
            return f"Connection to {url} timed out — the site may be down or very slow."
        if "dns" in err or "getaddrinfo" in err or "name resolution" in err:
            return f"DNS resolution failed for {url} — the domain may not exist or is misconfigured."
        if "403" in err or "forbidden" in err:
            return f"{url} returned a 403 Forbidden — the site is blocking automated access."
        if "404" in err or "not found" in err:
            return f"{url} returned a 404 Not Found — the URL may be incorrect."
        if "ssl" in err or "certificate" in err:
            return f"SSL/certificate error for {url} — the site may have an invalid certificate."
        if "connection refused" in err or "econnrefused" in err:
            return f"Connection refused by {url} — the server may be down."
        if "net::" in err or "network" in err:
            return f"Network error reaching {url} — the site may be unreachable."
        return f"Could not access {url}: {error_msg}"
