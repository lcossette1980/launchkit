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

        if not pages:
            self.logger.warning(
                "No pages to analyze for %s — crawler returned zero pages. "
                "Crawl errors: %s",
                config.get("site_url", "unknown"),
                state.get("crawl_errors", []),
            )
            state["page_analyses"] = []
            return state

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
                text_sample = re.sub(r"\s+", " ", text_sample)[:3000]
            except Exception:
                text_sample = ""

            perf = page.get("metrics", {})

            # Serialize structured data with priority ordering —
            # headings, CTAs, forms, and meta are most useful for analysis;
            # links and images are large arrays that can be truncated.
            sd = page.get("structured_data", {})
            priority_data = {
                "headings": sd.get("headings", []),
                "ctas": sd.get("ctas", []),
                "forms": sd.get("forms", []),
                "meta": sd.get("meta", {}),
            }
            secondary_data = {
                "links": sd.get("links", [])[:20],
                "images": sd.get("images", [])[:10],
            }
            structured_str = json.dumps(
                {**priority_data, **secondary_data}, indent=2
            )[:3000]

            # Check if this page has any broken outbound links
            broken_links = state.get("broken_links", [])
            page_broken = [
                bl for bl in broken_links
                if bl.get("source_page") == page["url"]
            ]
            broken_context = ""
            if page_broken:
                broken_urls = [f"{bl['url']} (HTTP {bl.get('status', '?')})" for bl in page_broken[:5]]
                broken_context = f"\n\nBROKEN LINKS FOUND ON THIS PAGE:\n" + "\n".join(broken_urls) + "\nInclude these in weaknesses and recommendations."

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
- Scores must be integers 0-100. Use this rubric consistently:
  CLARITY (how well the page communicates its purpose):
    90-100: Instantly clear value prop, no confusion about what this is/does
    70-89:  Purpose is clear but some messaging could be sharper
    50-69:  Takes effort to understand; mixed messages or vague copy
    30-49:  Confusing; unclear what the product/service is
    0-29:   No discernible message or purpose
  AUDIENCE_FIT (how well content matches the stated target audience):
    90-100: Every element speaks directly to target audience's language/needs
    70-89:  Good fit but some elements feel generic or off-target
    50-69:  Partially aligned; some content targets different personas
    30-49:  Weak alignment; mostly generic content
    0-29:   Content clearly targets a different audience
  CONVERSION (effectiveness at driving desired actions):
    90-100: Multiple clear CTAs, low friction, strong urgency/trust signals
    70-89:  CTAs present and visible but could be stronger/repeated
    50-69:  CTAs exist but weak visibility, missing trust signals, or high friction
    30-49:  Hard to find CTAs; significant conversion barriers
    0-29:   No clear conversion path
  SEO (search engine optimization quality):
    90-100: Excellent heading hierarchy, meta tags, keywords, structured data
    70-89:  Good basics but missing some optimization opportunities
    50-69:  Some SEO elements present but inconsistent or incomplete
    30-49:  Minimal SEO effort; missing critical elements
    0-29:   No SEO optimization visible
  UX (user experience and design quality):
    90-100: Smooth navigation, fast loading, accessible, polished design
    70-89:  Good UX with minor issues (layout, responsiveness, etc.)
    50-69:  Functional but noticeable UX problems (truncated text, poor nav, etc.)
    30-49:  Significant UX barriers that hurt engagement
    0-29:   Broken or unusable experience
- At least 3 items per list.
- Reference actual page elements (headings, CTAs, forms, copy) in your observations.

Page URL: {page['url']}
Title: {page.get('title', '')}
Performance (ms): loadTime={perf.get('loadTime', 'n/a')} domReady={perf.get('domReady', 'n/a')} firstPaint={perf.get('firstPaint', 'n/a')}
Structured Data:
{structured_str}
Visible Text:
{text_sample}{broken_context}"""

            analysis = await self._generate_json(
                prompt,
                required_keys=["strengths", "weaknesses", "recommendations", "scores"],
                min_counts={"strengths": 2, "weaknesses": 2, "recommendations": 2},
                brand=config["brand"],
                audience=config["audience_primary"],
            )

            # Vision analysis — if screenshot available, analyze visual design
            visual_observations: list[str] = []
            screenshot = page.get("screenshot")
            if screenshot and isinstance(screenshot, bytes):
                try:
                    vision_prompt = f"""Look at this screenshot of {page['url']} and analyze the VISUAL design.

Return ONLY valid JSON:
{{
  "visual_strengths": ["strength 1", "strength 2"],
  "visual_weaknesses": ["weakness 1", "weakness 2"],
  "visual_recommendations": ["recommendation 1", "recommendation 2"]
}}

Focus ONLY on what you can SEE:
- Is the CTA button prominent? What color is it? Does it stand out?
- Is there clear visual hierarchy? (headline > subheadline > body)
- Is the above-the-fold content compelling or cluttered?
- Are there too many competing elements?
- Is whitespace used effectively?
- Does the color scheme feel professional or amateur?
- Is text readable (contrast, size)?
- Does the hero section make the product clear within 3 seconds?

Be specific — reference what you actually see (colors, layout, size, position)."""

                    from gtm.llm.json_parser import extract_json
                    vision_raw = await self._generate_with_image(
                        vision_prompt,
                        screenshot,
                        brand=config["brand"],
                        audience=config["audience_primary"],
                    )
                    if vision_raw:
                        vision_data = extract_json(vision_raw)
                        if isinstance(vision_data, dict):
                            # Merge visual findings into main analysis
                            for vs in vision_data.get("visual_strengths", [])[:2]:
                                analysis.setdefault("strengths", []).append(f"[Visual] {vs}")
                            for vw in vision_data.get("visual_weaknesses", [])[:2]:
                                analysis.setdefault("weaknesses", []).append(f"[Visual] {vw}")
                            for vr in vision_data.get("visual_recommendations", [])[:2]:
                                analysis.setdefault("recommendations", []).append(f"[Visual] {vr}")
                            visual_observations = (
                                vision_data.get("visual_strengths", [])
                                + vision_data.get("visual_weaknesses", [])
                            )
                except Exception as e:
                    self.logger.warning("Vision analysis failed for %s: %s", page["url"], e)

            # Mobile vision analysis — homepage only
            mobile_screenshot = page.get("mobile_screenshot")
            if mobile_screenshot and isinstance(mobile_screenshot, bytes):
                try:
                    mobile_prompt = f"""Look at this MOBILE screenshot of {page['url']} (375px wide, iPhone).

Return ONLY valid JSON:
{{
  "mobile_issues": ["issue 1", "issue 2"],
  "mobile_strengths": ["strength 1"]
}}

Check:
- Is text readable without zooming?
- Do buttons/CTAs have adequate tap targets (44px minimum)?
- Is there horizontal scrolling (content wider than screen)?
- Is the navigation usable on mobile?
- Does the hero section work on a small screen?
- Is anything cut off, overlapping, or misaligned?"""

                    mobile_raw = await self._generate_with_image(
                        mobile_prompt,
                        mobile_screenshot,
                        brand=config["brand"],
                        audience=config["audience_primary"],
                    )
                    if mobile_raw:
                        mobile_data = extract_json(mobile_raw)
                        if isinstance(mobile_data, dict):
                            for mi in mobile_data.get("mobile_issues", [])[:2]:
                                analysis.setdefault("weaknesses", []).append(f"[Mobile] {mi}")
                            for ms in mobile_data.get("mobile_strengths", [])[:1]:
                                analysis.setdefault("strengths", []).append(f"[Mobile] {ms}")
                except Exception as e:
                    self.logger.warning("Mobile vision analysis failed: %s", e)

            analyses.append({
                "url": page["url"],
                "title": page.get("title", ""),
                "strengths": analysis.get("strengths", []),
                "weaknesses": analysis.get("weaknesses", []),
                "recommendations": analysis.get("recommendations", []),
                "scores": analysis.get("scores", {}),
                "quick_wins": analysis.get("quick_wins", []),
                "visual_observations": visual_observations,
            })

        state["page_analyses"] = analyses
        self.logger.info("Analyzed %d pages", len(analyses))

        # Auto-infer empty config fields from crawled homepage content
        await self._enrich_config_from_pages(state)

        return state

    async def _enrich_config_from_pages(self, state: dict) -> None:
        """Infer main_offers and usp_key from homepage if user left them empty."""
        config = state["config"]
        needs_offers = not config.get("main_offers", "").strip()
        needs_usp = not config.get("usp_key", "").strip()

        if not needs_offers and not needs_usp:
            return

        # Find homepage content from crawled pages
        pages = state.get("pages_crawled", [])
        homepage_text = ""
        for page in pages:
            url = page.get("url", "")
            # Homepage is typically the root URL or shortest path
            path = url.split("//")[-1].split("/", 1)[-1].strip("/")
            if not path or path == "":
                homepage_text = page.get("content", "")[:2000]
                break
        if not homepage_text and pages:
            homepage_text = pages[0].get("content", "")[:2000]

        if not homepage_text:
            return

        # Extract text only
        try:
            text = BeautifulSoup(homepage_text, "html.parser").get_text(separator=" ")
            text = re.sub(r"\s+", " ", text)[:1500]
        except Exception:
            return

        fields_needed = []
        if needs_offers:
            fields_needed.append('"main_offers": "the primary products or services offered"')
        if needs_usp:
            fields_needed.append('"usp_key": "the unique selling proposition or key differentiator"')

        prompt = f"""Based on this homepage text, identify the following. Return ONLY valid JSON:
{{
  {', '.join(fields_needed)}
}}

Be concise — each value should be 1-2 sentences max.
If you cannot determine a field from the text, use an empty string.

Homepage text:
{text}"""

        try:
            result = await self._generate_json(
                prompt,
                required_keys=[],
                brand=config.get("brand", ""),
            )
            if needs_offers and result.get("main_offers"):
                config["main_offers"] = result["main_offers"]
                self.logger.info("Auto-inferred main_offers: %s", result["main_offers"][:80])
            if needs_usp and result.get("usp_key"):
                config["usp_key"] = result["usp_key"]
                self.logger.info("Auto-inferred usp_key: %s", result["usp_key"][:80])
        except Exception:
            self.logger.warning("Config enrichment from homepage failed — continuing with empty fields")
