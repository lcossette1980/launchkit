"""Tests for agent base class and synthesizer logic."""

from gtm.agents.synthesizer import SynthesizerAgent
from gtm.schemas.analysis import WebsiteAnalysisSchema


class TestSynthesizerAggregation:
    """Test the synthesizer's non-LLM methods."""

    def test_aggregate_empty(self):
        agent = SynthesizerAgent.__new__(SynthesizerAgent)
        result = agent._aggregate_website_analysis([])
        assert isinstance(result, WebsiteAnalysisSchema)
        assert len(result.pages_analyzed) == 0
        assert result.overall_scores.clarity == 0

    def test_aggregate_single_page(self):
        agent = SynthesizerAgent.__new__(SynthesizerAgent)
        pages = [
            {
                "url": "https://example.com",
                "title": "Home",
                "strengths": ["Good design"],
                "weaknesses": ["Slow load"],
                "recommendations": ["Optimize images"],
                "scores": {"clarity": 80, "audience_fit": 70, "conversion": 60, "seo": 50, "ux": 90},
                "quick_wins": ["Add alt tags"],
            }
        ]
        result = agent._aggregate_website_analysis(pages)
        assert len(result.pages_analyzed) == 1
        assert result.overall_scores.clarity == 80
        assert result.overall_scores.ux == 90
        assert "Good design" in result.top_strengths

    def test_aggregate_averages_scores(self):
        agent = SynthesizerAgent.__new__(SynthesizerAgent)
        pages = [
            {"url": "a", "scores": {"clarity": 80, "audience_fit": 60, "conversion": 40, "seo": 20, "ux": 100}},
            {"url": "b", "scores": {"clarity": 40, "audience_fit": 80, "conversion": 60, "seo": 80, "ux": 0}},
        ]
        result = agent._aggregate_website_analysis(pages)
        assert result.overall_scores.clarity == 60  # (80+40)/2
        assert result.overall_scores.audience_fit == 70
        assert result.overall_scores.seo == 50

    def test_build_market_research(self):
        data = {
            "trends": ["AI growth"],
            "target_audience": "developers",
            "competitive_landscape": "fragmented",
            "keyword_opportunities": ["ai tools"],
            "content_topics": ["tutorials"],
        }
        result = SynthesizerAgent._build_market_research(data)
        assert result.trends == ["AI growth"]
        assert result.target_audience == "developers"

    def test_build_competitor_analysis(self):
        analyses = [
            {
                "url": "https://comp.com",
                "name": "Comp",
                "value_proposition": "Fast",
                "target_audience": "Devs",
                "pricing_model": "Free",
                "key_differentiators": ["Speed"],
                "strengths": ["Fast"],
                "weaknesses": ["No support"],
                "content_strategy": "Blog",
            }
        ]
        result = SynthesizerAgent._build_competitor_analysis(analyses)
        assert len(result.competitors) == 1
        assert result.competitors[0].name == "Comp"
