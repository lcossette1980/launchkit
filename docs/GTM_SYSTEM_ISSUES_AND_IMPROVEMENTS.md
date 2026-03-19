# GTM Analysis System — Issues, Improvements, and Fix Plan

## Overview
This document captures observed issues from a recent run (brand: "EvolvIQ") and maps them to root causes in code/design, then outlines concrete steps to fix. The goal is to make outputs specific, reliable, and reflective of the system’s agentic capabilities.

## Key Issues Observed
- Website analysis is thin
  - Only 1 page analyzed; sections like Strengths/Weaknesses/Recommendations are empty.
  - No clear page speed or accessibility evidence despite recommendations.
- Market research/competitors are off-target
  - Results conflate different brands (EvolvIQ vs Evolv AI/EvolutionIQ/EvoluteIQ).
  - Competitor URLs include directories or academic articles (e.g., MDPI, CBInsights pages), not direct service providers.
- Competitive analysis is generic
  - Conclusions are boilerplate and not grounded in on-page evidence.
- Strategy sections duplicate or misformat
  - 30-60-90 appears multiple times with repeated 30-day content.
- Experiments backlog missing
  - “No experiments available” despite the system having an experiments node.
- Copy & Messaging kit missing
  - “Copy kit pending”; no structured outputs (headlines, CTAs, emails, etc.).
- KPIs/Tracking generic
  - Metrics are not clearly tied back to funnel, offers, or audience specifics.

## Likely Root Causes (Code/Design)
- JSON outputs not guaranteed
  - Prompts ask for structured insights but do not enforce a strict JSON schema. Parsing failures return `{}` ⇒ empty sections.
  - See `LLMInterface._generate_openai` and calls in:
    - `analyze_pages` (no explicit schema in prompt)
    - `analyze_competitors` (no schema)
    - `create_experiments` (no schema)
    - `produce_copy` (no schema)
- Competitor discovery too naïve
  - Queries like "{brand} alternatives" or "companies like {brand}" cause brand collisions.
  - No semantic filtering or disambiguation; weak URL filtering lets through directories and research articles.
  - See `SearchTools.serp_search` + filtering logic in `research_market`.
- Crawl depth and discovery are fragile
  - Only first ~30 links from homepage; no sitemap.xml fallback; Playwright timeout is tight; no secondary fetch path.
  - See `crawl_website` and `WebTools.browse()`.
- Roadmap rendering scrapes text heuristically
  - `_format_roadmap_phase` searches for “30/60/90” strings instead of using structured fields.
- No QA/critic loop
  - Agents don’t validate coverage (e.g., empty strengths) or re-ask with a schema.

## High-Impact Improvements
- Enforce explicit schemas per task
  - Update prompts to include a strict JSON schema (keys + types) with “respond with only JSON”. Validate and re-prompt on failure.
- Add a critic/validator pass
  - After each LLM call, check required keys and minimal content. If missing, re-run with tighter instructions/temperature.
- Improve competitor discovery & relevance
  - Disambiguate brand entity (exact match "EvolvIQ"). Add negative keywords ("-weapons -security -EvolutionIQ -EvoluteIQ -Evolv AI").
  - Filter competitors to likely providers (has Services/Training/Consulting pages). Deprioritize directories and research articles.
  - Optionally re-rank candidates via semantic similarity to a brand/offers description.
- Strengthen crawling
  - Attempt `sitemap.xml` discovery; add `/about`, `/services`, `/pricing`, `/contact`, `/blog` fallbacks.
  - Add aiohttp + BeautifulSoup fallback when Playwright errors or is too slow; increase per-page timeout moderately.
- Make roadmap structured
  - Require `gtm_strategy.implementation_roadmap` with `{ "30_day": [...], "60_day": [...], "90_day": [...] }`. Render from that object, not text scraping.
- Add concrete page-speed/accessibility checks
  - Use existing `lighthouse`-like metrics to populate `performance_score`/`accessibility_score` and cite numeric values in recommendations.

## Step-by-Step Fix Plan
1) Tighten JSON generation and parsing (core)
- For each of these functions, add an explicit JSON schema in the prompt and require “return only JSON”. Set `temperature=0.3`.
  - `analyze_pages` ⇒ require: `{ strengths: string[], weaknesses: string[], recommendations: string[], scores: { clarity: number, audience_fit: number, conversion: number, seo: number, ux: number }, quick_wins: string[] }`
  - `analyze_competitors` ⇒ require: `{ value_proposition: string, target_audience: string, pricing_model: string, key_differentiators: string[], strengths: string[], weaknesses: string[], content_strategy: string }`
  - `generate_strategy` ⇒ require: `{ positioning: string[], channels: { primary: string[], secondary: string[] }, content_strategy: string[], partnerships: string[], pricing: string[], quick_wins: string[], implementation_roadmap: { "30_day": string[], "60_day": string[], "90_day": string[] } }`
  - `create_experiments` ⇒ require: `{ experiments: { title: string, hypothesis: string, metric: string, baseline: number|null, target: number|null, impact: number, confidence: number, effort: number, details: string }[] }`
  - `produce_copy` ⇒ require: `{ headlines: { headline: string, subheadline: string, cta: string }[], emails: {...}, linkedin_messages: {...}, ads: {...}, value_propositions: string[], landing_page_sections: { problem: string[], solution: string[], benefits: string[], social_proof: string[], faq: string[] } }`
  - `_create_dashboard_spec` ⇒ require: `{ north_star_metric: string, north_star_target: string, primary_kpis: string[], secondary_metrics: string[], tracking_requirements: string[], cadence: { daily: string[], weekly: string[], monthly: string[] }, alerts: { metric: string, threshold: string, action: string }[] }`
- Update `LLMInterface.generate` callers to pass `response_format="json"` consistently and lower `temperature` for structured tasks.
- Add a small utility to validate required keys and re-prompt once if missing.

2) Competitor discovery improvements (core)
- Query design: add exact brand disambiguation and negative keywords. Example:
  - `"\"EvolvIQ\" training consulting"`
  - `"AI workforce training providers site:.com"`
  - Add negatives: `-"Evolv AI" -EvolutionIQ -EvoluteIQ -weapons -security -g2 -cbinsights -trustradius` where appropriate.
- URL filtering: keep likely provider sites only
  - Drop news, directories, marketplaces, academic domains unless used in a separate “references” bucket.
  - Deduplicate by domain; prefer homepage or /services-like pages.
- Optional: simple LLM-based re-rank
  - Given brand/offers description and a candidate URL’s title/snippet, score 1–5 “provider relevance”. Keep top N.

3) Crawl robustness (core)
- Add sitemap discovery: fetch `/{sitemap.xml, sitemap_index.xml}` and parse for URLs.
- Add explicit fallbacks: try these if not discovered: `/about`, `/services`, `/pricing`, `/contact`, `/blog`.
- Playwright timeouts: raise to 20–30s for initial page; keep per-resource lightweight.
- Add aiohttp+BS4 fallback when Playwright returns error.

4) Roadmap rendering (UI)
- In report rendering, use `results.gtm_strategy.implementation_roadmap["30_day"|"60_day"|"90_day"]` if present; do not scrape from executive summary text.
- If missing, show a concise “not generated” line instead of repeating 30-day content.

5) Add a critic/QA layer (agentic boost)
- After each section:
  - Validate presence of required keys and minimum counts (e.g., ≥3 strengths, ≥3 recommendations).
  - If weak, re-run the prompt with more context or tighter instructions.
- Before synthesize, run a quick “consistency check”:
  - Deduplicate repeated items; flag contradictions; ensure competitors are service providers.

6) Evidence in recommendations (quality)
- When recommending speed/accessibility fixes, include numbers from `WebTools.browse().metrics` and `lighthouse()` where available.
- Cite analyzed page URLs next to page-specific findings.

## Validation Checklist (post-fix)
- Website analysis shows ≥5 pages with non-empty strengths/weaknesses/recommendations and numeric scores per category.
- Competitor list contains ≥3 true competitor providers (no directories/academic articles).
- Experiments section lists ≥10 experiments with ICE scores and sorted order.
- Copy kit populated (headlines, CTAs, emails, LinkedIn, ads, LP sections) with at least 3 hero variants.
- Roadmap renders correctly from structured data without duplicate sections.
- Metrics/alerts tie back to the offers/audience and reference the funnel.

## Optional Enhancements (Phase 2)
- Embedding-based semantic re-ranking of competitors/content topics.
- PageSpeed Insights API integration for lab data.
- Lightweight classifier to label domains as provider vs directory/news/academic.
- Persistent cache of sitemaps and crawl results by domain hash.
- “Benchmark diff” mode to compare current run with prior run for the same brand.

## Code Pointers
- gtm_system.py
  - LLM JSON handling: `LLMInterface._generate_openai`, `_generate_anthropic`
  - Orchestration: `OrchestratorAgent._build_workflow()` and subsequent steps
  - Crawling: `WebTools.browse`, `OrchestratorAgent.crawl_website`
  - Market research: `SearchTools.serp_search`, `OrchestratorAgent.research_market`
  - Competitor analysis: `OrchestratorAgent.analyze_competitors`
  - Experiments/Copy: `create_experiments`, `produce_copy`
  - Report rendering: `_format_roadmap_phase`, `_format_experiments`, `_format_copy_kit`

---

If you’d like, I can make targeted patches next: schema-enforced prompts, improved competitor filtering, structured roadmap rendering, and a basic QA validator.

## Progress Log
- 2025-09-06
  - Implemented schema-enforced prompts + basic validation for:
    - Page analysis, competitor analysis, GTM strategy, experiments, copy kit, dashboard spec.
  - Lowered temperatures for structured tasks to reduce variance.
  - Roadmap rendering now uses only `gtm_strategy.implementation_roadmap` (prevents duplication).
  - Competitor discovery improved with brand disambiguation, negative keywords, and stronger URL filtering.
  - Crawl step adds fallback URLs (/about, /services, /pricing, /contact, /blog, /solutions, /products) if discovery is thin.
  - Added centralized JSON validator helper and refactored core steps to use it.
  - Implemented sitemap discovery (sitemap.xml, sitemap_index.xml, robots.txt) to expand internal pages before crawling.
  - Configured S3 client to respect `AWS_ENDPOINT_URL` (MinIO) with s3v4 signing and added error handling to avoid task crashes.
  - Enhanced page analysis context with visible text snippets and performance metrics to ground recommendations.
  - Normalized input URLs to ensure proper scheme (https://) and avoid malformed `https:www...` in outputs.
  - Removed weak fallback slugs (`/service`, `/products`) and now only try common, likely pages.
  - Skip non-200 pages when adding to `pages_crawled` to avoid analyzing 404s.
  - Expanded competitor exclusion list (job boards, social networks, aggregators) to reduce noise.
  - Auto-interaction during crawl (tabs/modals) to reveal hidden content; prioritizes internal links using heading-derived tokens to catch pages like "why-ai-now" and "agentic-ai" without hardcoding.
  - Link discovery now scores internal URLs by token matches and common page types, expanding candidates beyond the first 30 links while still site-agnostic.
  - Build speed: switched Docker base to Playwright’s prebuilt image (chromium + deps) and added .dockerignore to avoid copying caches/logs; this dramatically reduces image build time.
  - OpenAI migration: switched to GPT-5 Responses API with `gpt-5-mini` across roles; added default reasoning effort and verbosity controls; preserved JSON-only enforcement in prompts.
  - Playwright fix: pinned Playwright Python to 1.55.0 and upgraded Docker base image to `mcr.microsoft.com/playwright/python:v1.55.0-jammy` to resolve browser executable mismatch.
  - Next: inject performance/accessibility metrics into recommendations and add aiohttp+BS4 page fallback when Playwright fails.

- 2025-09-08
  - **Enhanced Page Discovery & Crawling:**
    - Increased link discovery from 60 to 150 URLs for comprehensive site coverage
    - Added priority scoring for navigation and footer links (nav +5, footer +3 points)
    - Expanded important page patterns to include 'why-', 'how-', 'what-', 'ai', 'agentic', 'training'
    - Added more fallback paths including '/why-ai-now', '/agentic-ai', '/resources', '/case-studies'
  - **Interactive Content Extraction:**
    - Added _interact_with_page_elements() to WebTools to handle tabs, accordions, and expandables
    - Clicks role="tab", .tab-button, .nav-tabs, [data-toggle="tab"] elements
    - Expands accordions, collapsibles, and aria-expanded="false" elements
    - Clicks "Read More" buttons to reveal hidden content
    - Captures content states after each interaction for comprehensive analysis
  - **Competitor Targeting Enhancements:**
    - Added specific_competitors field for manual competitor URL input
    - Added competitor_keywords for targeted competitor searches
    - Added exclude_competitors for filtering out unwanted matches
    - Added max_competitors slider (3-10) to control analysis scope
    - Updated Gradio interface with new competitor targeting section
  - **Improved Link Context:**
    - Enhanced link extraction to capture is_navigation, is_footer, is_header context
    - Uses context for better prioritization during page discovery
  - **Known Issues Still to Address:**
    - WebTools interaction is best-effort; some dynamic content may still be missed
    - Need to implement multi-depth crawling for deeper site exploration
    - Could benefit from screenshot capture for visual analysis
    - Competitor analysis still limited to 3 by default (configurable now)
  - **Next Steps:**
    - Test with EvolvIQ site to verify all pages are discovered
    - Add visual content analysis using screenshots
    - Implement recursive crawling for deeper site structure
    - Add progress indicators for long-running analyses
