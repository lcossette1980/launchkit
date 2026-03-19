"""HTML report generator — converts FullReportSchema JSON into a styled report.

Fixed from original:
- Renamed all local `html` variables to `out` to avoid shadowing `import html`
- Aligned all keys to FullReportSchema (overall_scores, top_strengths, etc.)
- Scores are already 0-100 (no * 10 conversion)
- Module-level function accepts dict, not file path
"""

from __future__ import annotations

import html as html_mod
from datetime import datetime
from typing import Any

# Design system colors
COLORS = {
    "charcoal": "#2A2A2A",
    "chestnut": "#A44A3F",
    "khaki": "#A59E8C",
    "pearl": "#D7CEB2",
    "bone": "#F5F2EA",
}


def generate_html_report(results: dict[str, Any]) -> str:
    """Generate a complete HTML report from FullReportSchema-shaped data."""
    gen = _ReportBuilder(results)
    return gen.build()


class _ReportBuilder:
    """Internal builder that assembles the HTML sections."""

    def __init__(self, results: dict[str, Any]) -> None:
        self.results = results
        self.brand_info = results.get("brand_info", {})
        self.website = results.get("website_analysis", {})
        self.market = results.get("market_research", {})
        self.competitors = results.get("competitor_analysis", {})
        self.strategy = results.get("gtm_strategy", {})
        self.experiments = results.get("experiments", {})
        self.copy_kit = results.get("copy_kit", {})
        self.dashboard = results.get("dashboard", {})
        self.metadata = results.get("metadata", {})

    def build(self) -> str:
        brand = self.brand_info.get("brand", "Analysis")
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LaunchKit — GTM Playbook for {_esc(brand)}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
    <style>{_styles()}</style>
</head>
<body>
<div class="container">
    {self._header()}
    {self._executive_summary()}
    {self._website_analysis()}
    {self._market_insights()}
    {self._competitor_analysis()}
    {self._gtm_strategy()}
    {self._experiments_section()}
    {self._copy_kit_section()}
    {self._dashboard_spec()}
    {self._implementation_roadmap()}
    {self._footer()}
</div>
<script>{_javascript()}</script>
</body>
</html>"""

    # ------------------------------------------------------------------
    # Sections
    # ------------------------------------------------------------------

    def _header(self) -> str:
        brand = _esc(self.brand_info.get("brand", "Brand Analysis"))
        url = _esc(self.brand_info.get("url", ""))
        date = datetime.now().strftime("%B %d, %Y")
        return f"""
<div class="hero">
    <div class="hero-brand">Launch<span>Kit</span></div>
    <h1>GTM Playbook</h1>
    <div class="subtitle">{brand} &mdash; {url}</div>
    <div style="margin-top:1rem;opacity:0.85;font-size:0.9rem">Generated {date}</div>
</div>"""

    def _executive_summary(self) -> str:
        summary = self.results.get("executive_summary", {})
        brand = _esc(self.brand_info.get("brand", "The brand"))
        overview = _esc(summary.get("overview", "operates in a competitive market with significant growth potential."))
        pages_count = len(self.website.get("pages_analyzed", []))
        comp_count = len(self.competitors.get("competitors", []))
        exp_count = len(self.experiments.get("experiments", []))
        overall_score = self._calculate_overall_score()

        return f"""
<div class="section">
    <h2>Executive Summary</h2>
    <p><strong>{brand}</strong> {overview}</p>
    <div class="metric-grid">
        {_metric_card(str(pages_count), "Pages Analyzed")}
        {_metric_card(str(comp_count), "Competitors Analyzed")}
        {_metric_card(str(exp_count), "Experiments Proposed")}
        {_metric_card(f"{overall_score}%", "Overall Readiness")}
    </div>
    <h3>Key Findings</h3>
    {_bullet_list(summary.get("key_findings", ["Website analysis reveals opportunities for optimization", "Market positioning can be strengthened", "Clear GTM strategy identified with quick wins"]))}
    <h3>Top Priorities</h3>
    {_bullet_list(summary.get("top_priorities", []))}
</div>"""

    def _website_analysis(self) -> str:
        scores = self.website.get("overall_scores", {})
        return f"""
<div class="section">
    <h2>Website Analysis</h2>
    <h3>Overall Assessment</h3>
    <div class="metric-grid">
        {_score_card("Clarity", scores.get("clarity", 0))}
        {_score_card("Audience Fit", scores.get("audience_fit", 0))}
        {_score_card("Conversion", scores.get("conversion", 0))}
        {_score_card("SEO", scores.get("seo", 0))}
        {_score_card("UX", scores.get("ux", 0))}
    </div>
    <h3>Strengths</h3>
    {_bullet_list(self.website.get("top_strengths", []))}
    <h3>Areas for Improvement</h3>
    {_bullet_list(self.website.get("top_weaknesses", []))}
    <h3>Recommendations</h3>
    {_card_list(self.website.get("top_recommendations", []))}
    <h3>Quick Wins</h3>
    <div style="background:{COLORS['bone']};padding:1.5rem;border-radius:8px">
        {_numbered_list(self.website.get("quick_wins", []))}
    </div>
</div>"""

    def _market_insights(self) -> str:
        target = _esc(self.market.get("target_audience", "Professional organizations seeking AI transformation"))
        landscape = _esc(self.market.get("competitive_landscape", "The market is evolving rapidly."))
        return f"""
<div class="section">
    <h2>Market Insights</h2>
    <h3>Market Trends</h3>
    {_bullet_list(self.market.get("trends", []))}
    <h3>Target Audience</h3>
    <div class="list-item"><p>{target}</p></div>
    <h3>Competitive Landscape</h3>
    <p>{landscape}</p>
    <h3>Keyword Opportunities</h3>
    {_tag_list(self.market.get("keyword_opportunities", []))}
    <h3>Content Topics</h3>
    {_bullet_list(self.market.get("content_topics", []))}
</div>"""

    def _competitor_analysis(self) -> str:
        comps = self.competitors.get("competitors", [])
        return f"""
<div class="section">
    <h2>Competitor Analysis</h2>
    <div class="nav-tabs">
        <button class="nav-tab active" onclick="showTab('comp-overview')">Overview</button>
        <button class="nav-tab" onclick="showTab('comp-details')">Detailed Analysis</button>
        <button class="nav-tab" onclick="showTab('comp-matrix')">Comparison Matrix</button>
    </div>
    <div id="comp-overview" class="tab-content active">
        <h3>Key Competitors</h3>
        {_competitor_cards(comps[:3])}
    </div>
    <div id="comp-details" class="tab-content">
        <h3>Detailed Competitor Analysis</h3>
        {_detailed_competitors(comps)}
    </div>
    <div id="comp-matrix" class="tab-content">
        <h3>Competitive Comparison Matrix</h3>
        {_comparison_matrix(comps)}
    </div>
</div>"""

    def _gtm_strategy(self) -> str:
        channels = self.strategy.get("channels", {})
        return f"""
<div class="section">
    <h2>Go-To-Market Strategy</h2>
    <h3>Positioning</h3>
    {_bullet_list(self.strategy.get("positioning", []))}
    <h3>Channel Strategy</h3>
    <div class="metric-grid">
        <div class="metric-card">
            <h4>Primary Channels</h4>
            {_tag_list(channels.get("primary", []), "primary")}
        </div>
        <div class="metric-card">
            <h4>Secondary Channels</h4>
            {_tag_list(channels.get("secondary", []), "secondary")}
        </div>
    </div>
    <h3>Content Strategy</h3>
    {_bullet_list(self.strategy.get("content_strategy", []))}
    <h3>Pricing Strategy</h3>
    {_bullet_list(self.strategy.get("pricing", []))}
    <h3>Partnership Opportunities</h3>
    {_bullet_list(self.strategy.get("partnerships", []))}
</div>"""

    def _experiments_section(self) -> str:
        exp_list = self.experiments.get("experiments", [])
        out = """
<div class="section">
    <h2>Growth Experiments Backlog</h2>
    <p>Prioritized experiments based on ICE scoring (Impact, Confidence, Effort)</p>"""

        for exp in exp_list[:10]:
            title = _esc(exp.get("title", "Experiment"))
            hypothesis = _esc(exp.get("hypothesis", ""))
            metric = _esc(exp.get("metric", ""))
            details = _esc(exp.get("details", ""))
            ice = exp.get("ice_score", "")
            out += f"""
    <div class="experiment-card">
        <div class="experiment-header">
            <h4>{title}</h4>
            <div class="ice-scores">
                <div class="ice-score"><div class="label">Impact</div><div class="value">{exp.get("impact", 0)}</div></div>
                <div class="ice-score"><div class="label">Confidence</div><div class="value">{exp.get("confidence", 0)}</div></div>
                <div class="ice-score"><div class="label">Effort</div><div class="value">{exp.get("effort", 0)}</div></div>
                <div class="ice-score"><div class="label">ICE</div><div class="value">{ice}</div></div>
            </div>
        </div>
        <p><strong>Hypothesis:</strong> {hypothesis}</p>
        <p><strong>Metric:</strong> {metric}</p>
        <p>{details}</p>
    </div>"""

        out += "\n</div>"
        return out

    def _copy_kit_section(self) -> str:
        return f"""
<div class="section">
    <h2>Copy &amp; Messaging Kit</h2>
    <h3>Hero Headlines</h3>
    {_headline_blocks(self.copy_kit.get("headlines", []))}
    <h3>Value Propositions</h3>
    {_bullet_list(self.copy_kit.get("value_propositions", []))}
    <h3>Email Templates</h3>
    {_email_blocks(self.copy_kit.get("emails", {}))}
    <h3>LinkedIn Messages</h3>
    {_message_blocks(self.copy_kit.get("linkedin_messages", {}))}
    <h3>Ad Copy</h3>
    {_ad_blocks(self.copy_kit.get("ads", {}))}
</div>"""

    def _dashboard_spec(self) -> str:
        ns_metric = _esc(self.dashboard.get("north_star_metric", "Customer Activation Rate"))
        ns_target = _esc(self.dashboard.get("north_star_target", "80% within 30 days"))
        return f"""
<div class="section">
    <h2>Analytics Dashboard Specification</h2>
    <h3>North Star Metric</h3>
    <div class="metric-card" style="background:{COLORS['chestnut']};color:white">
        <h4 style="color:white">{ns_metric}</h4>
        <p>Target: {ns_target}</p>
    </div>
    <h3>Primary KPIs</h3>
    {_bullet_list(self.dashboard.get("primary_kpis", []))}
    <h3>Secondary Metrics</h3>
    {_bullet_list(self.dashboard.get("secondary_metrics", []))}
    <h3>Tracking Requirements</h3>
    {_bullet_list(self.dashboard.get("tracking_requirements", []))}
    <h3>Alert Thresholds</h3>
    {_alert_table(self.dashboard.get("alerts", []))}
</div>"""

    def _implementation_roadmap(self) -> str:
        roadmap = self.strategy.get("implementation_roadmap", {})
        return f"""
<div class="section">
    <h2>Implementation Roadmap</h2>
    <div class="timeline">
        <div class="timeline-item">
            <div class="timeline-period">First 30 Days</div>
            {_bullet_list(roadmap.get("30_day", roadmap.get("day_30", [])))}
        </div>
        <div class="timeline-item">
            <div class="timeline-period">30-60 Days</div>
            {_bullet_list(roadmap.get("60_day", roadmap.get("day_60", [])))}
        </div>
        <div class="timeline-item">
            <div class="timeline-period">60-90 Days</div>
            {_bullet_list(roadmap.get("90_day", roadmap.get("day_90", [])))}
        </div>
    </div>
</div>"""

    def _footer(self) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        job_id = _esc(self.metadata.get("job_id", ""))
        return f"""
<div class="footer">
    <p style="font-weight:600;color:{COLORS['chestnut']}">Generated by LaunchKit</p>
    <p>AI-powered GTM playbooks for builders &mdash; launchkit.dev</p>
    <p style="margin-top:0.5rem">{now}{f" &nbsp;|&nbsp; Report {job_id[:8]}" if job_id else ""}</p>
</div>"""

    def _calculate_overall_score(self) -> int:
        scores: list[float] = []
        website_scores = self.website.get("overall_scores", {})
        for v in website_scores.values():
            if isinstance(v, (int, float)) and v > 0:
                scores.append(float(v))  # Already 0-100
        if self.strategy:
            scores.append(80)
        if self.experiments.get("experiments"):
            scores.append(75)
        if self.copy_kit:
            scores.append(70)
        return int(sum(scores) / len(scores)) if scores else 50


# ------------------------------------------------------------------
# Helpers — all use `html_mod.escape` to avoid shadowing
# ------------------------------------------------------------------

def _esc(text: str) -> str:
    return html_mod.escape(str(text))


def _metric_card(value: str, label: str) -> str:
    return f"""<div class="metric-card">
    <div class="metric-value">{_esc(value)}</div>
    <div class="metric-label">{_esc(label)}</div>
</div>"""


def _score_card(label: str, score: int | float) -> str:
    score = min(100, max(0, int(score)))  # Already 0-100
    return f"""<div class="metric-card">
    <h4>{_esc(label)}</h4>
    <div class="metric-value">{score}%</div>
    <div class="score-bar"><div class="score-fill" style="width:{score}%"></div></div>
</div>"""


def _bullet_list(items: list) -> str:
    if not items:
        return "<p>No data available</p>"
    out = "<ul>"
    for item in items:
        out += f"<li>{_esc(str(item))}</li>"
    out += "</ul>"
    return out


def _numbered_list(items: list) -> str:
    if not items:
        return "<p>No data available</p>"
    out = "<ol>"
    for item in items:
        out += f"<li>{_esc(str(item))}</li>"
    out += "</ol>"
    return out


def _card_list(items: list) -> str:
    out = ""
    for item in items:
        out += f'<div class="list-item"><p>{_esc(str(item))}</p></div>'
    return out or "<p>No data available</p>"


def _tag_list(items: list, tag_class: str = "") -> str:
    if not items:
        return ""
    out = "<div>"
    for item in items:
        out += f'<span class="tag {tag_class}">{_esc(str(item))}</span>'
    out += "</div>"
    return out


def _competitor_cards(competitors: list) -> str:
    out = '<div class="metric-grid">'
    for comp in competitors:
        name = _esc(comp.get("name", "Competitor"))
        vp = _esc(comp.get("value_proposition", "N/A"))
        ta = _esc(comp.get("target_audience", "N/A"))
        out += f"""<div class="metric-card">
    <h4>{name}</h4>
    <p><strong>Focus:</strong> {vp}</p>
    <p><strong>Target:</strong> {ta}</p>
    {_tag_list(comp.get("key_differentiators", [])[:3])}
</div>"""
    out += "</div>"
    return out


def _detailed_competitors(competitors: list) -> str:
    out = ""
    for comp in competitors:
        name = _esc(comp.get("name", "Competitor"))
        vp = _esc(comp.get("value_proposition", "N/A"))
        strengths = ", ".join(_esc(s) for s in comp.get("strengths", []))
        weaknesses = ", ".join(_esc(w) for w in comp.get("weaknesses", []))
        cs = _esc(comp.get("content_strategy", "N/A"))
        out += f"""<div class="list-item">
    <h4>{name}</h4>
    <p><strong>Value Proposition:</strong> {vp}</p>
    <p><strong>Strengths:</strong> {strengths}</p>
    <p><strong>Weaknesses:</strong> {weaknesses}</p>
    <p><strong>Content Strategy:</strong> {cs}</p>
</div>"""
    return out


def _comparison_matrix(competitors: list) -> str:
    out = """<table><thead><tr>
    <th>Competitor</th><th>Target Audience</th><th>Pricing Model</th><th>Key Differentiators</th>
</tr></thead><tbody>"""
    for comp in competitors:
        name = _esc(comp.get("name", "N/A"))
        ta = _esc(comp.get("target_audience", "N/A"))
        pm = _esc(comp.get("pricing_model", "N/A"))
        diffs = ", ".join(_esc(d) for d in comp.get("key_differentiators", [])[:2])
        out += f"<tr><td><strong>{name}</strong></td><td>{ta}</td><td>{pm}</td><td>{diffs}</td></tr>"
    out += "</tbody></table>"
    return out


def _headline_blocks(headlines: list) -> str:
    out = ""
    for idx, headline in enumerate(headlines):
        if isinstance(headline, dict):
            text = f"{headline.get('headline', '')}\n{headline.get('subheadline', '')}"
            cta = headline.get("cta", "")
        else:
            text = str(headline)
            cta = ""
        safe_text = _esc(text)
        # Use data attribute for copy — avoids JS injection via single quotes
        out += f"""<div class="copy-block">
    <button class="copy-button" data-copy="{_esc(text)}" onclick="copyToClipboard(this.dataset.copy)">Copy</button>
    <h4>Option {idx + 1}</h4>
    <p>{safe_text}</p>
    {f'<p><strong>CTA:</strong> {_esc(cta)}</p>' if cta else ''}
</div>"""
    return out


def _email_blocks(emails: dict) -> str:
    out = ""
    for email_type, content in emails.items():
        if isinstance(content, dict):
            label = _esc(email_type.replace("_", " ").title())
            subject = _esc(content.get("subject", ""))
            body = _esc(content.get("body", ""))
            out += f"""<div class="copy-block">
    <h4>{label}</h4>
    <p><strong>Subject:</strong> {subject}</p>
    <p>{body}</p>
</div>"""
    return out


def _message_blocks(messages: dict) -> str:
    out = ""
    for msg_type, content in messages.items():
        label = _esc(msg_type.replace("_", " ").title())
        out += f"""<div class="copy-block">
    <h4>{label}</h4>
    <p>{_esc(str(content))}</p>
</div>"""
    return out


def _ad_blocks(ads: dict) -> str:
    out = ""
    for ad_type, content in ads.items():
        if isinstance(content, dict):
            label = _esc(ad_type.replace("_", " ").title())
            out += f"""<div class="copy-block">
    <h4>{label}</h4>
    <p><strong>Headline:</strong> {_esc(content.get('headline', ''))}</p>
    <p><strong>Description:</strong> {_esc(content.get('description', ''))}</p>
    <p><strong>CTA:</strong> {_esc(content.get('cta', ''))}</p>
</div>"""
    return out


def _alert_table(alerts: list) -> str:
    out = """<table><thead><tr>
    <th>Metric</th><th>Threshold</th><th>Action</th>
</tr></thead><tbody>"""
    for alert in alerts:
        if isinstance(alert, dict):
            out += f"""<tr>
    <td>{_esc(alert.get('metric', ''))}</td>
    <td>{_esc(str(alert.get('threshold', '')))}</td>
    <td>{_esc(alert.get('action', ''))}</td>
</tr>"""
    out += "</tbody></table>"
    return out


# ------------------------------------------------------------------
# CSS + JS (unchanged from original, just extracted as functions)
# ------------------------------------------------------------------

def _styles() -> str:
    return f"""
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Inter','Lato',sans-serif; font-weight:400; color:{COLORS['charcoal']}; background:{COLORS['bone']}; line-height:1.6; }}
.container {{ max-width:1200px; margin:0 auto; padding:20px; }}
h1,h2,h3,h4,h5,h6 {{ font-family:'Playfair Display',serif; font-weight:700; color:{COLORS['charcoal']}; margin-bottom:1rem; }}
h1 {{ font-size:2.6rem; margin-bottom:1.5rem; border-bottom:none; padding-bottom:0; }}
h2 {{ font-size:2rem; margin-top:3rem; margin-bottom:1.5rem; color:{COLORS['chestnut']}; }}
h3 {{ font-size:1.5rem; margin-top:2rem; margin-bottom:1rem; }}
h4 {{ font-size:1.2rem; margin-top:1.5rem; margin-bottom:0.8rem; color:{COLORS['khaki']}; }}
.section {{ background:#fff; padding:2rem; margin-bottom:2rem; border-radius:8px; box-shadow:0 2px 10px rgba(42,42,42,.1); }}
.hero {{ background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,{COLORS['chestnut']} 100%); color:#fff; padding:3.5rem 2rem 3rem; margin-bottom:3rem; border-radius:12px; text-align:center; }}
.hero h1 {{ color:#fff; border-bottom:none; margin-bottom:0.5rem; font-size:2.4rem; }}
.hero .subtitle {{ font-size:1.2rem; opacity:.85; font-weight:400; }}
.hero-brand {{ font-family:'Inter',sans-serif; font-size:0.9rem; font-weight:700; letter-spacing:1px; text-transform:uppercase; margin-bottom:1.2rem; opacity:.7; }}
.hero-brand span {{ color:{COLORS['pearl']}; }}
.metric-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:1.5rem; margin:2rem 0; }}
.metric-card {{ background:{COLORS['pearl']}; padding:1.5rem; border-radius:8px; text-align:center; transition:transform .3s ease; }}
.metric-card:hover {{ transform:translateY(-5px); box-shadow:0 5px 20px rgba(42,42,42,.15); }}
.metric-value {{ font-size:2.5rem; font-weight:700; color:{COLORS['chestnut']}; font-family:'Playfair Display',serif; }}
.metric-label {{ font-size:.9rem; text-transform:uppercase; letter-spacing:1px; color:{COLORS['charcoal']}; margin-top:.5rem; }}
.score-bar {{ height:8px; background:{COLORS['pearl']}; border-radius:4px; overflow:hidden; margin:.5rem 0; }}
.score-fill {{ height:100%; background:linear-gradient(90deg,{COLORS['chestnut']} 0%,{COLORS['khaki']} 100%); transition:width .5s ease; }}
.tag {{ display:inline-block; background:{COLORS['pearl']}; color:{COLORS['charcoal']}; padding:.3rem .8rem; border-radius:20px; font-size:.85rem; margin:.3rem; font-weight:500; }}
.tag.primary {{ background:{COLORS['chestnut']}; color:#fff; }}
.tag.secondary {{ background:{COLORS['khaki']}; color:#fff; }}
table {{ width:100%; border-collapse:collapse; margin:1.5rem 0; }}
th {{ background:{COLORS['khaki']}; color:#fff; padding:1rem; text-align:left; font-weight:500; }}
td {{ padding:1rem; border-bottom:1px solid {COLORS['pearl']}; }}
tr:hover {{ background:{COLORS['bone']}; }}
.list-item {{ padding:1rem; margin:.5rem 0; background:{COLORS['bone']}; border-left:4px solid {COLORS['chestnut']}; border-radius:4px; }}
.list-item h4 {{ margin-top:0; }}
.timeline {{ position:relative; padding-left:3rem; }}
.timeline::before {{ content:''; position:absolute; left:1rem; top:0; bottom:0; width:2px; background:{COLORS['khaki']}; }}
.timeline-item {{ position:relative; margin-bottom:2rem; }}
.timeline-item::before {{ content:''; position:absolute; left:-2.4rem; top:.5rem; width:12px; height:12px; border-radius:50%; background:{COLORS['chestnut']}; border:3px solid #fff; box-shadow:0 0 0 3px {COLORS['pearl']}; }}
.timeline-period {{ font-weight:700; color:{COLORS['chestnut']}; font-size:1.2rem; margin-bottom:.5rem; }}
.experiment-card {{ background:#fff; border:1px solid {COLORS['pearl']}; border-radius:8px; padding:1.5rem; margin:1rem 0; }}
.experiment-header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; flex-wrap:wrap; gap:.5rem; }}
.ice-scores {{ display:flex; gap:1rem; flex-wrap:wrap; }}
.ice-score {{ background:{COLORS['bone']}; padding:.5rem 1rem; border-radius:4px; text-align:center; }}
.ice-score .label {{ font-size:.75rem; text-transform:uppercase; color:{COLORS['khaki']}; }}
.ice-score .value {{ font-size:1.2rem; font-weight:700; color:{COLORS['chestnut']}; }}
.copy-block {{ background:{COLORS['bone']}; padding:1.5rem; border-radius:8px; margin:1rem 0; position:relative; }}
.copy-block h4 {{ margin-top:0; }}
.copy-button {{ position:absolute; top:1rem; right:1rem; background:{COLORS['chestnut']}; color:#fff; border:none; padding:.5rem 1rem; border-radius:4px; cursor:pointer; font-size:.85rem; transition:background .3s ease; }}
.copy-button:hover {{ background:{COLORS['khaki']}; }}
.nav-tabs {{ display:flex; border-bottom:2px solid {COLORS['pearl']}; margin-bottom:2rem; }}
.nav-tab {{ padding:1rem 2rem; background:none; border:none; cursor:pointer; font-size:1rem; font-weight:500; color:{COLORS['khaki']}; transition:all .3s ease; }}
.nav-tab.active {{ color:{COLORS['chestnut']}; border-bottom:3px solid {COLORS['chestnut']}; margin-bottom:-2px; }}
.tab-content {{ display:none; }}
.tab-content.active {{ display:block; }}
.footer {{ text-align:center; padding:3rem 0; margin-top:4rem; border-top:1px solid {COLORS['pearl']}; color:{COLORS['khaki']}; }}
ul, ol {{ margin:0.5rem 0 1rem 1.5rem; }}
li {{ margin-bottom:0.3rem; }}
@media print {{ .copy-button {{ display:none; }} .section {{ break-inside:avoid; }} }}
"""


def _javascript() -> str:
    return """
function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    event.target.classList.add('active');
}
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        event.target.textContent = 'Copied!';
        setTimeout(() => { event.target.textContent = 'Copy'; }, 2000);
    });
}
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) { entry.target.style.opacity='1'; entry.target.style.transform='translateY(0)'; }
    });
}, { threshold: 0.1, rootMargin: '0px 0px -100px 0px' });
document.querySelectorAll('.metric-card').forEach(card => {
    card.style.opacity='0'; card.style.transform='translateY(20px)'; card.style.transition='all 0.5s ease';
    observer.observe(card);
});
"""
