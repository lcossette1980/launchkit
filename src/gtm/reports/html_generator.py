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
    <title>VCLaunchKit — GTM Playbook for {_esc(brand)}</title>
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
    <div class="hero-brand">VC<span>LaunchKit</span></div>
    <h1>GTM Playbook</h1>
    <div class="subtitle">{brand} &mdash; {url}</div>
    <div style="margin-top:1rem;opacity:0.85;font-size:0.9rem">Generated {date}</div>
</div>"""

    def _executive_summary(self) -> str:
        summary = self.results.get("executive_summary", {})
        brand = _esc(self.brand_info.get("brand", "The brand"))
        overview = _esc(summary.get("overview", ""))
        pages_count = len(self.website.get("pages_analyzed", []))
        comp_count = len(self.competitors.get("competitors", []))
        exp_count = len(self.experiments.get("experiments", []))
        overall_score = self._calculate_overall_score()

        # Executive Snapshot — the founder-grade opening
        biggest_problem = _esc(summary.get("biggest_problem", ""))
        biggest_opportunity = _esc(summary.get("biggest_opportunity", ""))
        best_next_move = _esc(summary.get("best_next_move", ""))
        expected_impact = _esc(summary.get("expected_impact", ""))
        top_3 = summary.get("top_3_actions", [])

        snapshot = ""
        if biggest_problem:
            snapshot = f"""
    <div class="exec-snapshot">
        <div class="snapshot-grid">
            <div class="snapshot-item problem">
                <div class="snapshot-label">Biggest Problem</div>
                <p>{biggest_problem}</p>
            </div>
            <div class="snapshot-item opportunity">
                <div class="snapshot-label">Biggest Opportunity</div>
                <p>{biggest_opportunity}</p>
            </div>
            <div class="snapshot-item next-move">
                <div class="snapshot-label">Best Next Move</div>
                <p>{best_next_move}</p>
            </div>
            <div class="snapshot-item impact">
                <div class="snapshot-label">Expected Impact</div>
                <p>{expected_impact}</p>
            </div>
        </div>
    </div>"""

        actions_html = ""
        if top_3:
            actions_items = ""
            for i, action in enumerate(top_3[:3], 1):
                actions_items += f'<div class="action-item"><span class="action-num">{i}</span><p>{_esc(str(action))}</p></div>'
            actions_html = f"""
    <div class="top-actions">
        <h3>Your Top 3 Actions for the Next 14 Days</h3>
        {actions_items}
    </div>"""

        return f"""
<div class="section">
    <h2>Executive Summary</h2>
    {snapshot}
    {actions_html}
    <div class="metric-grid">
        {_metric_card(str(pages_count), "Pages Analyzed")}
        {_metric_card(str(comp_count), "Competitors")}
        {_metric_card(str(exp_count), "Experiments")}
        {_metric_card(f"{overall_score}%", "Readiness")}
    </div>
    {f'<h3>Overview</h3><p>{overview}</p>' if overview else ''}
    <h3>Key Findings</h3>
    {_bullet_list(summary.get("key_findings", []))}
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
        target = _esc(self.market.get("target_audience", ""))
        landscape = _esc(self.market.get("competitive_landscape", ""))
        trends = self.market.get("trends", [])
        keywords = self.market.get("keyword_opportunities", [])
        topics = self.market.get("content_topics", [])

        # Compress: only show target audience + keywords + top 5 topics
        # Skip generic trends and landscape paragraphs that add little value
        out = """<div class="section">\n    <h2>Market Context</h2>"""
        if target:
            out += f'\n    <h3>Target Audience</h3>\n    <div class="list-item"><p>{target}</p></div>'
        if landscape:
            out += f'\n    <h3>Competitive Landscape</h3>\n    <p>{landscape}</p>'
        if keywords:
            out += f'\n    <h3>Keyword Opportunities</h3>\n    {_tag_list(keywords[:10])}'
        if topics:
            out += f'\n    <h3>Content Topics</h3>\n    {_bullet_list(topics[:5])}'
        out += "\n</div>"
        return out

    def _competitor_analysis(self) -> str:
        comps = self.competitors.get("competitors", [])

        # If no competitors or only 1 weak result, show a minimal section
        if not comps:
            return ""
        if len(comps) == 1:
            return f"""
<div class="section">
    <h2>Competitor Snapshot</h2>
    <p style="color:{COLORS['khaki']};font-style:italic">Limited competitor data available. Consider expanding the analysis with manually identified competitors.</p>
    {_competitor_cards(comps)}
</div>"""

        # Full competitor section for 2+ competitors
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
        {_competitor_cards(comps[:5])}
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
        top_experiments = exp_list[:5]
        remaining = exp_list[5:]
        out = """
<div class="section">
    <h2>Growth Experiments</h2>
    <p>Top 5 experiments ranked by ICE score (Impact &times; Confidence &div; Effort)</p>"""

        for exp in top_experiments:
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
        <p style="font-size:0.78rem"><strong>Hypothesis:</strong> {hypothesis}</p>
        <p style="font-size:0.78rem"><strong>Metric:</strong> {metric}</p>
        <p style="font-size:0.78rem;color:#555">{details}</p>
    </div>"""

        # Compact list of remaining experiments
        if remaining:
            out += '\n    <h3 style="margin-top:2rem">Additional Experiments</h3>'
            out += '\n    <table><thead><tr><th>Experiment</th><th>ICE</th><th>Impact</th><th>Effort</th></tr></thead><tbody>'
            for exp in remaining:
                out += f'<tr><td>{_esc(exp.get("title", ""))}</td><td><strong>{exp.get("ice_score", "")}</strong></td><td>{exp.get("impact", "")}</td><td>{exp.get("effort", "")}</td></tr>'
            out += '</tbody></table>'

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
    <p style="font-weight:600;color:{COLORS['chestnut']}">Generated by VCLaunchKit</p>
    <p>AI-powered GTM playbooks for builders &mdash; vclaunchkit.com</p>
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
body {{ font-family:'Inter','Lato',sans-serif; font-weight:400; color:{COLORS['charcoal']}; background:#fff; line-height:1.55; font-size:9.5pt; }}
.container {{ max-width:860px; margin:0 auto; padding:16px 20px; }}
h1,h2,h3,h4,h5,h6 {{ font-family:'Playfair Display',serif; font-weight:700; color:{COLORS['charcoal']}; margin-bottom:0.4rem; }}
h1 {{ font-size:1.4rem; margin-bottom:0.6rem; border-bottom:none; padding-bottom:0; }}
h2 {{ font-size:1.15rem; margin-top:1.4rem; margin-bottom:0.6rem; color:{COLORS['chestnut']}; padding-bottom:0.25rem; border-bottom:1.5px solid {COLORS['pearl']}; }}
h3 {{ font-size:0.95rem; margin-top:0.9rem; margin-bottom:0.4rem; }}
h4 {{ font-size:0.88rem; margin-top:0.6rem; margin-bottom:0.3rem; color:{COLORS['khaki']}; }}
p {{ margin-bottom:0.35rem; font-size:0.88rem; line-height:1.5; }}
.section {{ background:#fff; padding:1rem 1.2rem; margin-bottom:0.8rem; border-radius:5px; border:1px solid {COLORS['pearl']}; }}
.hero {{ background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,{COLORS['chestnut']} 100%); color:#fff; padding:1.2rem 1.4rem 1rem; margin-bottom:1.2rem; border-radius:6px; text-align:center; }}
.hero h1 {{ color:#fff; border-bottom:none; margin-bottom:0.2rem; font-size:1.3rem; }}
.hero .subtitle {{ font-size:0.82rem; opacity:.85; font-weight:400; }}
.hero-brand {{ font-family:'Inter',sans-serif; font-size:0.65rem; font-weight:700; letter-spacing:1px; text-transform:uppercase; margin-bottom:0.5rem; opacity:.7; }}
.hero-brand span {{ color:{COLORS['pearl']}; }}

/* Executive snapshot */
.exec-snapshot {{ margin:0.6rem 0; }}
.snapshot-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:0.5rem; }}
.snapshot-item {{ padding:0.6rem 0.7rem; border-radius:4px; border-left:3px solid {COLORS['khaki']}; background:{COLORS['bone']}; }}
.snapshot-item.problem {{ border-left-color:{COLORS['chestnut']}; }}
.snapshot-item.opportunity {{ border-left-color:#4a7c59; }}
.snapshot-item.next-move {{ border-left-color:#2a6496; }}
.snapshot-item.impact {{ border-left-color:{COLORS['khaki']}; }}
.snapshot-label {{ font-size:0.62rem; text-transform:uppercase; letter-spacing:0.5px; font-weight:700; color:{COLORS['khaki']}; margin-bottom:0.15rem; }}
.snapshot-item.problem .snapshot-label {{ color:{COLORS['chestnut']}; }}
.snapshot-item.opportunity .snapshot-label {{ color:#4a7c59; }}
.snapshot-item.next-move .snapshot-label {{ color:#2a6496; }}
.snapshot-item p {{ font-size:0.78rem; line-height:1.4; margin:0; }}

/* Top 3 actions */
.top-actions {{ margin:0.8rem 0; padding:0.8rem; background:{COLORS['bone']}; border-radius:5px; }}
.top-actions h3 {{ margin-top:0; font-size:0.9rem; color:{COLORS['chestnut']}; }}
.action-item {{ display:flex; align-items:flex-start; gap:0.5rem; margin:0.4rem 0; }}
.action-num {{ display:flex; align-items:center; justify-content:center; min-width:1.3rem; height:1.3rem; background:{COLORS['chestnut']}; color:#fff; border-radius:50%; font-size:0.65rem; font-weight:700; flex-shrink:0; }}
.action-item p {{ margin:0; font-size:0.8rem; line-height:1.4; }}

.metric-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(120px,1fr)); gap:0.6rem; margin:0.6rem 0; }}
.metric-card {{ background:{COLORS['bone']}; padding:0.6rem; border-radius:5px; text-align:center; }}
.metric-value {{ font-size:1.15rem; font-weight:700; color:{COLORS['chestnut']}; font-family:'Playfair Display',serif; }}
.metric-label {{ font-size:0.6rem; text-transform:uppercase; letter-spacing:0.5px; color:{COLORS['charcoal']}; margin-top:0.15rem; }}
.score-bar {{ height:4px; background:{COLORS['pearl']}; border-radius:2px; overflow:hidden; margin:.2rem 0; }}
.score-fill {{ height:100%; background:linear-gradient(90deg,{COLORS['chestnut']} 0%,{COLORS['khaki']} 100%); }}
.tag {{ display:inline-block; background:{COLORS['pearl']}; color:{COLORS['charcoal']}; padding:.15rem .5rem; border-radius:10px; font-size:.68rem; margin:.15rem; font-weight:500; }}
.tag.primary {{ background:{COLORS['chestnut']}; color:#fff; }}
.tag.secondary {{ background:{COLORS['khaki']}; color:#fff; }}
table {{ width:100%; border-collapse:collapse; margin:0.6rem 0; font-size:0.78rem; }}
th {{ background:{COLORS['khaki']}; color:#fff; padding:0.35rem 0.5rem; text-align:left; font-weight:600; font-size:0.72rem; }}
td {{ padding:0.35rem 0.5rem; border-bottom:1px solid {COLORS['pearl']}; }}
tr:hover {{ background:{COLORS['bone']}; }}
.list-item {{ padding:0.5rem 0.7rem; margin:.25rem 0; background:{COLORS['bone']}; border-left:3px solid {COLORS['chestnut']}; border-radius:3px; }}
.list-item h4 {{ margin-top:0; }}
.timeline {{ position:relative; padding-left:1.8rem; }}
.timeline::before {{ content:''; position:absolute; left:0.55rem; top:0; bottom:0; width:2px; background:{COLORS['khaki']}; }}
.timeline-item {{ position:relative; margin-bottom:0.8rem; }}
.timeline-item::before {{ content:''; position:absolute; left:-1.55rem; top:.35rem; width:7px; height:7px; border-radius:50%; background:{COLORS['chestnut']}; border:2px solid #fff; box-shadow:0 0 0 2px {COLORS['pearl']}; }}
.timeline-period {{ font-weight:700; color:{COLORS['chestnut']}; font-size:0.85rem; margin-bottom:.2rem; }}
.experiment-card {{ background:#fff; border:1px solid {COLORS['pearl']}; border-radius:5px; padding:0.6rem 0.7rem; margin:0.4rem 0; }}
.experiment-header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:0.3rem; flex-wrap:wrap; gap:.3rem; }}
.experiment-header h4 {{ margin:0; font-size:0.82rem; }}
.ice-scores {{ display:flex; gap:0.4rem; flex-wrap:wrap; }}
.ice-score {{ background:{COLORS['bone']}; padding:.2rem .45rem; border-radius:3px; text-align:center; }}
.ice-score .label {{ font-size:.55rem; text-transform:uppercase; color:{COLORS['khaki']}; }}
.ice-score .value {{ font-size:0.78rem; font-weight:700; color:{COLORS['chestnut']}; }}
.copy-block {{ background:{COLORS['bone']}; padding:0.6rem 0.7rem; border-radius:5px; margin:0.4rem 0; position:relative; }}
.copy-block h4 {{ margin-top:0; font-size:0.78rem; }}
.copy-button {{ position:absolute; top:0.4rem; right:0.4rem; background:{COLORS['chestnut']}; color:#fff; border:none; padding:.2rem .5rem; border-radius:3px; cursor:pointer; font-size:.62rem; }}
.copy-button:hover {{ background:{COLORS['khaki']}; }}
.nav-tabs {{ display:flex; border-bottom:1.5px solid {COLORS['pearl']}; margin-bottom:0.8rem; }}
.nav-tab {{ padding:.4rem .8rem; background:none; border:none; cursor:pointer; font-size:.78rem; font-weight:500; color:{COLORS['khaki']}; }}
.nav-tab.active {{ color:{COLORS['chestnut']}; border-bottom:2px solid {COLORS['chestnut']}; margin-bottom:-1.5px; }}
.tab-content {{ display:none; }}
.tab-content.active {{ display:block; }}
.footer {{ text-align:center; padding:1.2rem 0; margin-top:1.5rem; border-top:1px solid {COLORS['pearl']}; color:{COLORS['khaki']}; font-size:0.7rem; }}
ul, ol {{ margin:0.25rem 0 0.5rem 1.1rem; font-size:0.8rem; }}
li {{ margin-bottom:0.15rem; line-height:1.4; }}
@page {{ size:A4; margin:1.8cm 1.5cm; }}
@media print {{
    .copy-button {{ display:none; }}
    .section {{ break-inside:avoid; page-break-inside:avoid; border:none; padding:0.6rem 0; margin-bottom:0.4rem; }}
    .hero {{ padding:0.8rem; margin-bottom:0.8rem; -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
    .nav-tabs {{ display:none; }}
    .tab-content {{ display:block !important; }}
    body {{ font-size:8.5pt; }}
    .container {{ padding:0; }}
    p {{ font-size:0.82rem; }}
    ul, ol {{ font-size:0.78rem; }}
}}
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
