"""Web crawling tools using Playwright.

Ported from the original gtm_system.py WebTools class — the crawling
intelligence, interactive element handling, and structured data extraction
are preserved as-is since they work well.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from playwright.async_api import Browser, Page, async_playwright

logger = logging.getLogger(__name__)


class WebTools:
    """Real web interaction tools using Playwright."""

    def __init__(self) -> None:
        self.browser: Browser | None = None
        self.context: Any = None
        self.page: Page | None = None
        self._playwright: Any = None

    async def initialize(self) -> None:
        """Initialize browser instance."""
        self._playwright = await async_playwright().start()
        self.browser = await self._playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        self.page = await self.context.new_page()

    async def close(self) -> None:
        """Close browser instance."""
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def browse(self, url: str, *, enable_interaction: bool = True) -> dict:
        """Navigate to URL and extract content with optional interactive handling."""
        try:
            response = await self.page.goto(
                url, wait_until="domcontentloaded", timeout=25000
            )
            # Wait for network idle to ensure React/SPA content is fully rendered
            try:
                await self.page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                # Fall back gracefully if networkidle times out (e.g. streaming pages)
                await asyncio.sleep(2)
            await asyncio.sleep(1)  # Extra buffer for late-rendering components

            if enable_interaction:
                await self._interact_with_page_elements()

            content = await self.page.content()
            title = await self.page.title()

            metrics = await self.page.evaluate(
                """() => {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    return {
                        loadTime: perfData ? perfData.loadEventEnd - perfData.fetchStart : 0,
                        domReady: perfData ? perfData.domContentLoadedEventEnd - perfData.fetchStart : 0,
                        firstPaint: (performance.getEntriesByName('first-paint')[0] || {}).startTime || 0
                    };
                }"""
            )

            structured_data = await self._extract_structured_data()

            # Limit content size to prevent API errors
            if len(content) > 100000:
                content = content[:100000] + "<!-- Content truncated -->"

            return {
                "url": url,
                "status": response.status if response else 200,
                "title": title,
                "content": content,
                "metrics": metrics,
                "structured_data": structured_data,
            }

        except Exception as e:
            logger.error("Error browsing %s: %s", url, e)
            return {"url": url, "error": str(e)}

    async def _interact_with_page_elements(self) -> None:
        """Interact with tabs, accordions, and expandable elements."""
        try:
            await asyncio.wait_for(self._do_interact(), timeout=10)
        except asyncio.TimeoutError:
            logger.debug("Interactive element handling timed out — continuing")
        except Exception as e:
            logger.debug("Error interacting with page elements: %s", e)

    async def _do_interact(self) -> None:
        """Inner implementation of page interaction (called with timeout)."""
        try:
                # Dismiss cookie banners
                for selector in [
                    '[data-cookiefirst-action="accept"]',
                    'button:has-text("Accept")',
                    'button:has-text("Accept all")',
                    ".cookie-accept",
                    "#accept-cookies",
                ]:
                    try:
                        btn = await self.page.query_selector(selector)
                        if btn and await btn.is_visible():
                            await btn.click(timeout=1000)
                            await asyncio.sleep(0.5)
                            break
                    except Exception:
                        pass

                # Click visible tabs
                for selector in [
                    '[role="tab"]:visible',
                    ".tab-button:visible",
                    ".nav-tabs a:visible",
                    '[data-toggle="tab"]:visible',
                ]:
                    try:
                        tabs = await self.page.query_selector_all(selector)
                        for tab in tabs[:10]:
                            try:
                                await tab.click()
                                await asyncio.sleep(0.3)
                            except Exception:
                                continue
                    except Exception:
                        continue

                # Expand accordions and collapsibles
                for selector in [
                    '[data-toggle="collapse"]:visible',
                    ".accordion-button:visible",
                    '[aria-expanded="false"]:visible',
                    "details:not([open]) summary",
                ]:
                    try:
                        elements = await self.page.query_selector_all(selector)
                        for element in elements[:10]:
                            try:
                                await element.click()
                                await asyncio.sleep(0.2)
                            except Exception:
                                continue
                    except Exception:
                        continue

                # Click "Read More" buttons
                try:
                    buttons = await self.page.query_selector_all("text=/read more/i")
                    for button in buttons[:5]:
                        try:
                            await button.click()
                            await asyncio.sleep(0.2)
                        except Exception:
                            continue
                except Exception:
                    pass

        except Exception:
            pass  # Errors handled by caller's wait_for

    async def _extract_structured_data(self) -> dict:
        """Extract structured data from current page via JS evaluation."""
        return await self.page.evaluate(
            """() => {
                const headings = Array.from(document.querySelectorAll('h1, h2, h3')).map(h => ({
                    level: h.tagName,
                    text: (h.textContent || '').trim()
                }));

                const links = Array.from(document.querySelectorAll('a[href]')).map(a => ({
                    text: (a.textContent || '').trim(),
                    href: a.href,
                    external: !a.href.includes(window.location.hostname),
                    is_navigation: a.closest('nav') !== null || a.closest('[role="navigation"]') !== null,
                    is_footer: a.closest('footer') !== null,
                    is_header: a.closest('header') !== null
                }));

                const images = Array.from(document.querySelectorAll('img')).map(img => ({
                    src: img.src,
                    alt: img.alt,
                    width: img.naturalWidth,
                    height: img.naturalHeight
                }));

                const forms = Array.from(document.querySelectorAll('form')).map(form => ({
                    action: form.action,
                    method: form.method,
                    fields: Array.from(form.querySelectorAll('input, select, textarea')).map(f => ({
                        type: f.type || f.tagName.toLowerCase(),
                        name: f.name,
                        required: f.required
                    }))
                }));

                const ctas = Array.from(document.querySelectorAll(
                    'button, .btn, .button, [class*="cta"], [href*="contact"], [href*="demo"], [href*="trial"]'
                ))
                    .map(el => (el.textContent || '').trim())
                    .filter(text => text.length > 0 && text.length < 200);

                const meta = {};
                document.querySelectorAll('meta').forEach(tag => {
                    if (tag.name) meta[tag.name] = tag.content;
                    if (tag.property) meta[tag.property] = tag.content;
                });

                return {
                    headings,
                    links: links.slice(0, 100),
                    images: images.slice(0, 50),
                    forms,
                    ctas: [...new Set(ctas)],
                    meta
                };
            }"""
        )

    async def screenshot(self, url: str, path: str | None = None) -> bytes:
        """Take full-page screenshot."""
        await self.page.goto(url, wait_until="networkidle")
        data = await self.page.screenshot(full_page=True)
        if path:
            with open(path, "wb") as f:
                f.write(data)
        return data
