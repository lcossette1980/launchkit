"""Tests for the HTML report generator.

Verifies:
- No html variable shadowing crash
- All sections render without error
- Keys align with FullReportSchema
- XSS-relevant content is escaped
"""

from gtm.reports.html_generator import generate_html_report


class TestHtmlGenerator:
    def test_generates_without_error(self, sample_report):
        result = generate_html_report(sample_report)
        assert isinstance(result, str)
        assert "<!DOCTYPE html>" in result

    def test_brand_in_title(self, sample_report):
        result = generate_html_report(sample_report)
        assert "TestBrand" in result

    def test_scores_rendered(self, sample_report):
        result = generate_html_report(sample_report)
        assert "75%" in result  # clarity score
        assert "80%" in result  # audience_fit score

    def test_experiments_rendered(self, sample_report):
        result = generate_html_report(sample_report)
        assert "Homepage CTA test" in result
        assert "28.0" in result  # ICE score

    def test_copy_kit_rendered(self, sample_report):
        result = generate_html_report(sample_report)
        assert "Ship faster with AI guidance" in result

    def test_roadmap_rendered(self, sample_report):
        result = generate_html_report(sample_report)
        assert "Set up analytics" in result
        assert "First 30 Days" in result

    def test_empty_report_does_not_crash(self):
        result = generate_html_report({})
        assert "<!DOCTYPE html>" in result

    def test_xss_escaped(self):
        malicious = {
            "brand_info": {
                "brand": '<script>alert("xss")</script>',
                "url": "https://evil.com",
            },
            "executive_summary": {
                "overview": '<img onerror="alert(1)" src=x>',
                "key_findings": ['<b>bold</b> finding'],
            },
        }
        result = generate_html_report(malicious)
        # The injected brand name should be escaped in user-content areas
        assert '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;' in result
        assert 'onerror=&quot;alert' in result
        assert "&lt;b&gt;bold&lt;/b&gt;" in result

    def test_competitor_tabs_rendered(self, sample_report):
        result = generate_html_report(sample_report)
        assert "comp-overview" in result
        assert "CompetitorA" in result

    def test_dashboard_alerts_rendered(self, sample_report):
        result = generate_html_report(sample_report)
        assert "Signup rate" in result
        assert "Review landing page" in result
