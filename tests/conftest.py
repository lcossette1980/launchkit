"""Shared test fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture()
def sample_config() -> dict:
    """Minimal analysis config for testing."""
    return {
        "site_url": "https://example.com",
        "brand": "TestBrand",
        "audience_primary": "indie developers",
        "audience_secondary": "startup founders",
        "main_offers": "AI consulting",
        "usp_key": "speed and simplicity",
        "business_size": "Solopreneur",
        "monthly_budget": "$500-$2000",
        "analysis_depth": "comprehensive",
        "max_pages_to_scan": 10,
        "max_competitors": 3,
    }


@pytest.fixture()
def sample_report() -> dict:
    """A complete FullReportSchema-shaped dict for testing."""
    return {
        "brand_info": {
            "brand": "TestBrand",
            "url": "https://example.com",
            "audience_primary": "indie developers",
            "audience_secondary": "startup founders",
            "main_offers": "AI consulting",
            "usp_key": "speed and simplicity",
            "business_size": "Solopreneur",
            "monthly_budget": "$500-$2000",
        },
        "executive_summary": {
            "overview": "TestBrand operates in the AI consulting space.",
            "key_findings": [
                "Strong technical content",
                "Weak CTA placement",
                "SEO opportunities exist",
            ],
            "top_priorities": [
                "Improve homepage CTA",
                "Add pricing page",
                "Start content marketing",
            ],
        },
        "website_analysis": {
            "pages_analyzed": [
                {
                    "url": "https://example.com",
                    "title": "TestBrand - Home",
                    "strengths": ["Clear value prop"],
                    "weaknesses": ["No pricing"],
                    "recommendations": ["Add pricing page"],
                    "scores": {
                        "clarity": 75,
                        "audience_fit": 80,
                        "conversion": 60,
                        "seo": 55,
                        "ux": 70,
                    },
                    "quick_wins": ["Add CTA above fold"],
                }
            ],
            "overall_scores": {
                "clarity": 75,
                "audience_fit": 80,
                "conversion": 60,
                "seo": 55,
                "ux": 70,
            },
            "top_strengths": ["Clear value prop"],
            "top_weaknesses": ["No pricing"],
            "top_recommendations": ["Add pricing page"],
            "quick_wins": ["Add CTA above fold"],
        },
        "market_research": {
            "trends": ["AI adoption accelerating"],
            "target_audience": "Indie developers building AI products",
            "competitive_landscape": "Fragmented market with few specialists",
            "keyword_opportunities": ["ai consulting for devs"],
            "content_topics": ["AI product launch guide"],
        },
        "competitor_analysis": {
            "competitors": [
                {
                    "url": "https://competitor.com",
                    "name": "CompetitorA",
                    "value_proposition": "Enterprise AI solutions",
                    "target_audience": "Large enterprises",
                    "pricing_model": "Custom",
                    "key_differentiators": ["Scale"],
                    "strengths": ["Brand recognition"],
                    "weaknesses": ["Expensive"],
                    "content_strategy": "Whitepapers and webinars",
                }
            ]
        },
        "gtm_strategy": {
            "positioning": ["The developer-first AI consultancy"],
            "channels": {
                "primary": ["Twitter/X", "Dev.to"],
                "secondary": ["LinkedIn"],
            },
            "content_strategy": ["Weekly technical blog posts"],
            "partnerships": ["Developer tool companies"],
            "pricing": ["Free tier for open source projects"],
            "quick_wins": ["Launch landing page"],
            "implementation_roadmap": {
                "30_day": ["Set up analytics"],
                "60_day": ["Launch blog"],
                "90_day": ["First paid campaign"],
            },
        },
        "experiments": {
            "experiments": [
                {
                    "title": "Homepage CTA test",
                    "hypothesis": "If we move CTA above fold, conversions increase",
                    "metric": "conversion_rate",
                    "impact": 8,
                    "confidence": 7,
                    "effort": 2,
                    "ice_score": 28.0,
                    "details": "A/B test current vs above-fold CTA",
                }
            ]
        },
        "copy_kit": {
            "headlines": [
                {
                    "headline": "Ship faster with AI guidance",
                    "subheadline": "Expert GTM strategy for solo devs",
                    "cta": "Get Started",
                }
            ],
            "value_propositions": ["Developer-first approach"],
            "emails": {
                "welcome": {
                    "subject": "Welcome to TestBrand",
                    "body": "Thanks for signing up!",
                }
            },
            "linkedin_messages": {
                "connection_request": "Hi, I noticed you build AI tools..."
            },
            "ads": {
                "google_search": {
                    "headline": "AI GTM Strategy",
                    "description": "Get your app to market",
                    "cta": "Learn More",
                }
            },
            "landing_page_sections": {
                "problem": ["Getting users is hard"],
                "solution": ["We make it easy"],
                "benefits": ["Save time"],
                "social_proof": ["100+ devs served"],
                "faq": ["Q: How long? A: 2 weeks"],
            },
        },
        "dashboard": {
            "north_star_metric": "Weekly Active Users",
            "north_star_target": "1000 in 90 days",
            "primary_kpis": ["Signup rate", "Activation rate"],
            "secondary_metrics": ["Page views"],
            "tracking_requirements": ["Google Analytics 4"],
            "cadence": {"daily": ["Signups"], "weekly": ["Retention"], "monthly": ["Revenue"]},
            "alerts": [
                {
                    "metric": "Signup rate",
                    "threshold": "< 2%",
                    "action": "Review landing page",
                }
            ],
        },
        "metadata": {
            "job_id": "test-job-123",
            "analysis_depth": "comprehensive",
            "pages_crawled": 1,
            "competitors_analyzed": 1,
        },
    }
