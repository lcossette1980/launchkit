import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getAnalysis, getReportUrl, createShareLink, getShareInfo } from "../api/analyses";
import { createCheckout } from "../api/billing";
import type { FullReport, Scores } from "../types/api";

function ShareButton({ jobId }: { jobId: string }) {
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    getShareInfo(jobId).then((info) => {
      if (info.share_url) setShareUrl(window.location.origin + info.share_url);
    }).catch(() => {});
  }, [jobId]);

  const handleShare = async () => {
    if (shareUrl) {
      navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      return;
    }
    setLoading(true);
    try {
      const res = await createShareLink(jobId);
      const url = window.location.origin + res.share_url;
      setShareUrl(url);
      navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      alert("Failed to create share link");
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleShare}
      disabled={loading}
      className={`text-xs border rounded-lg px-3 py-1.5 transition-colors ${
        copied
          ? "border-success text-success"
          : shareUrl
          ? "border-accent text-accent2 hover:bg-accent/10"
          : "border-border text-text2 hover:border-accent hover:text-accent2"
      }`}
    >
      {loading ? "..." : copied ? "Link Copied!" : shareUrl ? "Copy Share Link" : "Share"}
    </button>
  );
}

function scoreColor(v: number) {
  if (v >= 75) return "text-success";
  if (v >= 50) return "text-warning";
  return "text-danger";
}
function barColor(v: number) {
  if (v >= 75) return "bg-success";
  if (v >= 50) return "bg-warning";
  return "bg-danger";
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center gap-2 py-0.5">
      <span className="text-xs text-text2 w-20 shrink-0">{label}</span>
      <div className="flex-1 h-1.5 bg-surface rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${barColor(value)}`} style={{ width: `${value}%` }} />
      </div>
      <span className={`text-xs font-bold w-7 text-right ${scoreColor(value)}`}>{value}</span>
    </div>
  );
}

function CopyBtn({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={() => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 1500); }}
      className="text-[10px] text-text2 border border-border rounded px-1.5 py-0.5 hover:border-accent hover:text-accent2 transition-colors shrink-0"
    >
      {copied ? "Copied!" : "Copy"}
    </button>
  );
}

function PaywallLock({ title, onUpgrade }: { title: string; onUpgrade: () => void }) {
  return (
    <div className="relative my-4">
      <div className="blur-sm opacity-40 pointer-events-none select-none bg-surface border border-border rounded-xl p-6">
        <p className="text-sm text-text2">{title} — detailed analysis, actionable recommendations, and tactical insights...</p>
        <div className="h-20" />
      </div>
      <div className="absolute inset-0 flex flex-col items-center justify-center bg-bg/70 rounded-xl">
        <span className="text-2xl mb-2">&#128274;</span>
        <p className="font-semibold text-sm">{title}</p>
        <p className="text-xs text-text2 mb-3">Upgrade to Pro to unlock</p>
        <button onClick={onUpgrade} className="px-4 py-2 bg-accent text-white text-xs font-semibold rounded-lg hover:bg-accent2 transition-colors">
          Upgrade — $29/mo
        </button>
      </div>
    </div>
  );
}

function Section({ id, title, children }: { id: string; title: string; children: React.ReactNode }) {
  return (
    <section id={id} className="mb-6 scroll-mt-20">
      <h3 className="text-xs font-semibold text-accent2 uppercase tracking-wider mb-3 pb-2 border-b border-border">{title}</h3>
      {children}
    </section>
  );
}

function RecList({ items, icon, color }: { items: string[]; icon: string; color: string }) {
  return (
    <div className="space-y-1">
      {items.map((item, i) => (
        <div key={i} className="flex gap-2.5 py-1.5 border-b border-border/50 last:border-0 text-sm leading-relaxed">
          <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5 ${color}`}>{icon}</span>
          <span>{item}</span>
        </div>
      ))}
    </div>
  );
}

export default function ResultsPage() {
  const { id } = useParams<{ id: string }>();
  useAuth(); // ensure authenticated
  const [report, setReport] = useState<FullReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    getAnalysis(id)
      .then(setReport)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  const handleUpgrade = async () => {
    try {
      const res = await createCheckout("pro");
      window.location.href = res.checkout_url;
    } catch { /* ignore */ }
  };

  if (loading) return <div className="max-w-5xl mx-auto px-5 py-12"><div className="animate-pulse text-text2">Loading results...</div></div>;
  if (error) return <div className="max-w-5xl mx-auto px-5 py-12"><p className="text-danger">{error}</p><Link to="/dashboard" className="text-accent2 text-sm mt-4 inline-block">Back to Dashboard</Link></div>;
  if (!report) return null;

  const isTeaser = report._teaser === true;
  const exec = report.executive_summary ?? {};
  const web = report.website_analysis ?? {};
  const market = report.market_research ?? {};
  const comp = report.competitor_analysis?.competitors ?? [];
  const strategy = report.gtm_strategy ?? {};
  const copy = report.copy_kit ?? {};
  const dashboard = report.dashboard ?? {};
  const scores = web.overall_scores ?? {} as Scores;
  const pages = web.pages_analyzed ?? [];
  const roadmap = strategy.implementation_roadmap ?? {};
  const crawlFailed = web.crawl_failed === true || web.overall_scores === null;
  const scoresAreEmpty = !web.overall_scores || Object.values(web.overall_scores).every(v => v === 0);

  const SECTIONS = [
    "Summary", "Scores", ...(pages.length ? ["Pages"] : []),
    ...(market.target_audience ? ["Market"] : []),
    ...(comp.length ? ["Competitors"] : []),
    ...(strategy.positioning ? ["Strategy"] : []),
    ...(roadmap["30_day"]?.length ? ["Roadmap"] : []),
    ...(copy.headlines?.length ? ["Copy Kit"] : []),
    ...(copy.emails ? ["Outreach"] : []),
    ...(dashboard.north_star_metric ? ["KPIs"] : []),
  ];

  return (
    <div className="max-w-5xl mx-auto px-5 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
        <div>
          <Link to="/dashboard" className="text-xs text-text2 hover:text-accent2 mb-1 inline-block">&larr; Dashboard</Link>
          <h1 className="text-2xl font-bold">{report.brand_info?.brand ?? "GTM Playbook"}</h1>
        </div>
        <div className="flex gap-2">
          <ShareButton jobId={id!} />
          <a href={getReportUrl(id!, "pdf")} target="_blank" className="text-xs border border-border rounded-lg px-3 py-1.5 text-text2 hover:border-accent hover:text-accent2 transition-colors">PDF</a>
          <a href={getReportUrl(id!, "html")} target="_blank" className="text-xs border border-border rounded-lg px-3 py-1.5 text-text2 hover:border-accent hover:text-accent2 transition-colors">HTML</a>
          <a href={getReportUrl(id!, "json")} target="_blank" className="text-xs border border-border rounded-lg px-3 py-1.5 text-text2 hover:border-accent hover:text-accent2 transition-colors">JSON</a>
        </div>
      </div>

      {/* Section nav */}
      <div className="flex gap-1.5 flex-wrap mb-6 pb-4 border-b border-border sticky top-14 bg-bg/95 backdrop-blur-sm z-10 pt-2">
        {SECTIONS.map((s) => (
          <button
            key={s}
            onClick={() => document.getElementById(`sec-${s.toLowerCase()}`)?.scrollIntoView({ behavior: "smooth", block: "start" })}
            className="px-3 py-1.5 text-xs font-medium text-text2 border border-border rounded-md hover:border-accent hover:text-accent2 transition-colors"
          >
            {s}
          </button>
        ))}
      </div>

      {/* ══ EXECUTIVE SUMMARY ══ */}
      <Section id="sec-summary" title="Executive Summary">
        {crawlFailed && (
          <div className="bg-warning/10 border border-warning/40 rounded-xl p-5 mb-3">
            <div className="flex gap-2.5 items-start">
              <span className="text-warning text-lg shrink-0">&#9888;</span>
              <div>
                <p className="font-semibold text-sm text-warning mb-1">Website Crawl Failed</p>
                <p className="text-sm leading-relaxed">
                  We were unable to crawl this website. The site may be down, blocking automated access, or the URL may be incorrect.
                  Website-specific scores and page analysis are unavailable. The market research, competitor analysis, and strategy sections below are still based on publicly available information.
                </p>
                {web.crawl_errors && web.crawl_errors.length > 0 && (
                  <ul className="mt-2 text-xs text-text2 space-y-1 list-disc pl-4">
                    {web.crawl_errors.map((err, i) => <li key={i}>{err}</li>)}
                  </ul>
                )}
              </div>
            </div>
          </div>
        )}
        {exec.overview && <div className="bg-surface border border-border rounded-xl p-5 mb-3"><p className="text-sm leading-relaxed">{exec.overview}</p></div>}
        {exec.top_priorities && exec.top_priorities.length > 0 && (
          <div className="bg-surface border border-border rounded-xl p-5">
            <p className="font-semibold text-sm mb-3">Top Priorities</p>
            {exec.top_priorities.map((p, i) => (
              <div key={i} className="flex gap-2.5 py-1.5 border-b border-border/50 last:border-0 text-sm">
                <span className="w-5 h-5 rounded-full bg-accent/15 text-accent2 flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">{i + 1}</span>
                <span>{p}</span>
              </div>
            ))}
          </div>
        )}
      </Section>

      {/* ══ WEBSITE SCORES ══ */}
      {(crawlFailed || scoresAreEmpty) && (
        <Section id="sec-scores" title="Website Scores">
          <div className="bg-warning/10 border border-warning/40 rounded-xl p-5 mb-4">
            <div className="flex gap-2.5 items-start">
              <span className="text-warning text-lg shrink-0">&#9888;</span>
              <div>
                <p className="font-semibold text-sm text-warning mb-1">Scores Unavailable</p>
                <p className="text-sm text-text2">
                  {"We couldn't fully analyze this website. The site may be down, blocking automated access, or the URL may be incorrect. Website scores could not be generated for this analysis."}
                </p>
              </div>
            </div>
          </div>
        </Section>
      )}
      {!crawlFailed && !scoresAreEmpty && Object.keys(scores).length > 0 && (
        <Section id="sec-scores" title="Website Scores">
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mb-4">
            {Object.entries(scores).map(([k, v]) => (
              <div key={k} className="bg-surface border border-border rounded-xl p-4 text-center">
                <div className={`text-2xl font-bold ${scoreColor(v)}`}>{v}</div>
                <div className="text-[10px] text-text2 uppercase tracking-wider mt-1">{k.replace(/_/g, " ")}</div>
              </div>
            ))}
          </div>
          {web.top_strengths && web.top_strengths.length > 0 && (
            <div className="bg-surface border border-border rounded-xl p-5 mb-3">
              <p className="font-semibold text-sm text-success mb-2">Strengths</p>
              <RecList items={web.top_strengths} icon="+" color="bg-success/15 text-success" />
            </div>
          )}
          {web.top_weaknesses && web.top_weaknesses.length > 0 && (
            <div className="bg-surface border border-border rounded-xl p-5 mb-3">
              <p className="font-semibold text-sm text-danger mb-2">Weaknesses</p>
              <RecList items={web.top_weaknesses} icon="!" color="bg-danger/15 text-danger" />
            </div>
          )}
          {web.quick_wins && web.quick_wins.length > 0 && (
            <div className="bg-surface border border-border rounded-xl p-5">
              <p className="font-semibold text-sm text-warning mb-2">Quick Wins</p>
              <RecList items={web.quick_wins} icon="*" color="bg-warning/15 text-warning" />
            </div>
          )}
        </Section>
      )}

      {/* ══ PER-PAGE ANALYSIS ══ */}
      {isTeaser && !pages.length && <PaywallLock title="Page-by-Page Analysis (19 pages)" onUpgrade={handleUpgrade} />}
      {pages.length > 0 && (
        <Section id="sec-pages" title={`Page Analysis (${pages.length} pages)`}>
          {pages.map((pg, idx) => {
            const avg = Object.values(pg.scores).reduce((a, b) => a + b, 0) / Object.values(pg.scores).length;
            return (
              <details key={idx} className="bg-surface border border-border rounded-xl mb-2 group" open={idx === 0}>
                <summary className="px-5 py-3 cursor-pointer flex items-center justify-between">
                  <div className="min-w-0">
                    <p className="text-xs text-accent2 truncate">{pg.url}</p>
                    <p className="text-sm font-semibold truncate">{pg.title}</p>
                  </div>
                  <span className={`text-xs font-bold px-2 py-0.5 rounded-full shrink-0 ml-3 ${avg >= 70 ? "bg-success/15 text-success" : avg >= 50 ? "bg-warning/15 text-warning" : "bg-danger/15 text-danger"}`}>
                    Avg {Math.round(avg)}
                  </span>
                </summary>
                <div className="px-5 pb-4 border-t border-border pt-3 space-y-3">
                  <div>{Object.entries(pg.scores).map(([k, v]) => <ScoreBar key={k} label={k.replace(/_/g, " ")} value={v} />)}</div>
                  {pg.strengths?.length > 0 && <><p className="text-[10px] font-bold text-success uppercase">Strengths</p><RecList items={pg.strengths} icon="+" color="bg-success/15 text-success" /></>}
                  {pg.weaknesses?.length > 0 && <><p className="text-[10px] font-bold text-danger uppercase mt-2">Weaknesses</p><RecList items={pg.weaknesses} icon="!" color="bg-danger/15 text-danger" /></>}
                  {pg.recommendations?.length > 0 && <><p className="text-[10px] font-bold text-accent2 uppercase mt-2">Recommendations</p><RecList items={pg.recommendations} icon=">" color="bg-accent/15 text-accent2" /></>}
                  {pg.quick_wins?.length > 0 && <><p className="text-[10px] font-bold text-warning uppercase mt-2">Quick Wins</p><RecList items={pg.quick_wins} icon="*" color="bg-warning/15 text-warning" /></>}
                </div>
              </details>
            );
          })}
        </Section>
      )}

      {/* ══ MARKET RESEARCH ══ */}
      {isTeaser && !market.target_audience && <PaywallLock title="Market Research" onUpgrade={handleUpgrade} />}
      {market.target_audience && (
        <Section id="sec-market" title="Market Research">
          <div className="bg-surface border border-border rounded-xl p-5 mb-3">
            <p className="font-semibold text-sm mb-1">Target Audience</p>
            <p className="text-sm text-text2">{market.target_audience}</p>
          </div>
          {market.competitive_landscape && (
            <div className="bg-surface border border-border rounded-xl p-5 mb-3">
              <p className="font-semibold text-sm mb-1">Competitive Landscape</p>
              <p className="text-sm text-text2">{market.competitive_landscape}</p>
            </div>
          )}
          {market.keyword_opportunities && market.keyword_opportunities.length > 0 && (
            <div className="bg-surface border border-border rounded-xl p-5 mb-3">
              <p className="font-semibold text-sm mb-2">Keyword Opportunities</p>
              <div className="flex flex-wrap gap-1.5">{market.keyword_opportunities.map((k, i) => <span key={i} className="text-xs px-2.5 py-1 border border-border rounded-full bg-surface2">{k}</span>)}</div>
            </div>
          )}
          {market.content_topics && market.content_topics.length > 0 && (
            <div className="bg-surface border border-border rounded-xl p-5">
              <p className="font-semibold text-sm mb-2">Content Topics</p>
              <ul className="text-sm text-text2 space-y-1 list-disc pl-4">{market.content_topics.map((t, i) => <li key={i}>{t}</li>)}</ul>
            </div>
          )}
        </Section>
      )}

      {/* ══ COMPETITORS ══ */}
      {isTeaser && !comp.length && <PaywallLock title="Competitor Analysis" onUpgrade={handleUpgrade} />}
      {comp.length > 0 && (
        <Section id="sec-competitors" title={`Competitors (${comp.length})`}>
          {comp.map((c, i) => (
            <details key={i} className="bg-surface border border-border rounded-xl mb-2">
              <summary className="px-5 py-3 cursor-pointer flex items-center justify-between">
                <span className="font-semibold text-sm">{c.name}</span>
                {c.url && <a href={c.url} target="_blank" rel="noopener" className="text-[10px] text-accent2 hover:underline" onClick={(e) => e.stopPropagation()}>Visit</a>}
              </summary>
              <div className="px-5 pb-4 border-t border-border pt-3 space-y-2 text-sm">
                {c.value_proposition && <p><strong className="text-text2">Value Prop:</strong> {c.value_proposition}</p>}
                {c.target_audience && <p><strong className="text-text2">Target:</strong> {c.target_audience}</p>}
                {c.pricing_model && <p><strong className="text-text2">Pricing:</strong> {c.pricing_model}</p>}
                {c.strengths && c.strengths.length > 0 && <><p className="text-[10px] font-bold text-success uppercase mt-2">Strengths</p><RecList items={c.strengths} icon="+" color="bg-success/15 text-success" /></>}
                {c.weaknesses && c.weaknesses.length > 0 && <><p className="text-[10px] font-bold text-danger uppercase mt-2">Weaknesses</p><RecList items={c.weaknesses} icon="!" color="bg-danger/15 text-danger" /></>}
              </div>
            </details>
          ))}
        </Section>
      )}

      {/* ══ GTM STRATEGY ══ */}
      {isTeaser && !strategy.positioning && <PaywallLock title="GTM Strategy & Roadmap" onUpgrade={handleUpgrade} />}
      {strategy.positioning && (
        <Section id="sec-strategy" title="GTM Strategy">
          <div className="bg-surface border border-border rounded-xl p-5 mb-3">
            <p className="font-semibold text-sm mb-2">Positioning</p>
            <ul className="text-sm space-y-1 list-disc pl-4">{strategy.positioning.map((p, i) => <li key={i}>{p}</li>)}</ul>
          </div>
          {strategy.channels && (
            <div className="bg-surface border border-border rounded-xl p-5 mb-3">
              <p className="font-semibold text-sm mb-2">Channels</p>
              {strategy.channels.primary && <><p className="text-[10px] text-success font-bold uppercase mb-1">Primary</p><div className="flex flex-wrap gap-1.5 mb-3">{strategy.channels.primary.map((c, i) => <span key={i} className="text-xs px-2.5 py-1 border border-success/30 rounded-full">{c}</span>)}</div></>}
              {strategy.channels.secondary && <><p className="text-[10px] text-text2 font-bold uppercase mb-1">Secondary</p><div className="flex flex-wrap gap-1.5">{strategy.channels.secondary.map((c, i) => <span key={i} className="text-xs px-2.5 py-1 border border-border rounded-full">{c}</span>)}</div></>}
            </div>
          )}
          {strategy.pricing && strategy.pricing.length > 0 && (
            <div className="bg-surface border border-border rounded-xl p-5">
              <p className="font-semibold text-sm mb-2">Pricing Recommendations</p>
              <RecList items={strategy.pricing} icon="$" color="bg-success/15 text-success" />
            </div>
          )}
        </Section>
      )}

      {/* ══ ROADMAP ══ */}
      {roadmap["30_day"]?.length && (
        <Section id="sec-roadmap" title="Implementation Roadmap">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {(["30_day", "60_day", "90_day"] as const).map((key) => {
              const items = roadmap[key] ?? [];
              const label = key.replace("_", " ").replace("day", "Days");
              return items.length > 0 ? (
                <div key={key} className="bg-surface border border-border rounded-xl p-5">
                  <h4 className="text-xs font-bold text-accent2 mb-3 uppercase">{label}</h4>
                  <ul className="text-sm space-y-1.5 list-disc pl-4">{items.map((item, i) => <li key={i}>{item}</li>)}</ul>
                </div>
              ) : null;
            })}
          </div>
        </Section>
      )}

      {/* ══ COPY KIT ══ */}
      {isTeaser && !copy.headlines?.length && <PaywallLock title="Copy Kit, Emails & Ads" onUpgrade={handleUpgrade} />}
      {copy.headlines && copy.headlines.length > 0 && (
        <Section id="sec-copy kit" title="Copy Kit">
          {copy.headlines.map((h, i) => (
            <div key={i} className="bg-surface border border-border rounded-xl p-5 mb-2 relative">
              <p className="font-bold text-base">{h.headline}</p>
              {h.subheadline && <p className="text-sm text-text2 mt-1">{h.subheadline}</p>}
              {h.cta && <span className="inline-block mt-2 text-[10px] px-2 py-0.5 rounded bg-accent/15 text-accent2 font-semibold">{h.cta}</span>}
              <div className="absolute top-3 right-3"><CopyBtn text={`${h.headline}\n${h.subheadline ?? ""}\nCTA: ${h.cta ?? ""}`} /></div>
            </div>
          ))}
          {copy.value_propositions && copy.value_propositions.length > 0 && (
            <div className="bg-surface border border-border rounded-xl p-5 mt-3">
              <p className="font-semibold text-sm mb-2">Value Propositions</p>
              <ul className="text-sm space-y-1 list-disc pl-4">{copy.value_propositions.map((v, i) => <li key={i}>{v}</li>)}</ul>
            </div>
          )}
        </Section>
      )}

      {/* ══ OUTREACH ══ */}
      {copy.emails && Object.keys(copy.emails).length > 0 && (
        <Section id="sec-outreach" title="Emails & Outreach">
          {Object.entries(copy.emails).map(([type, email]) => (
            <div key={type} className="bg-surface border border-border rounded-xl p-5 mb-2 relative">
              <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-accent/15 text-accent2 mb-2 inline-block">
                {type.replace(/_/g, " ")}
              </span>
              <p className="text-sm font-semibold mb-2">Subject: {email.subject}</p>
              <pre className="text-sm text-text2 whitespace-pre-line leading-relaxed">{email.body}</pre>
              <div className="absolute top-3 right-3"><CopyBtn text={`Subject: ${email.subject}\n\n${email.body}`} /></div>
            </div>
          ))}
          {copy.linkedin_messages && Object.keys(copy.linkedin_messages).length > 0 && (
            <div className="bg-surface border border-border rounded-xl p-5 mt-3">
              <p className="font-semibold text-sm mb-3">LinkedIn Messages</p>
              {Object.entries(copy.linkedin_messages).map(([type, msg]) => (
                <div key={type} className="pb-3 mb-3 border-b border-border/50 last:border-0 last:mb-0 last:pb-0">
                  <span className="text-[10px] font-bold uppercase text-success">{type.replace(/_/g, " ")}</span>
                  <p className="text-sm text-text2 mt-1">{msg}</p>
                </div>
              ))}
            </div>
          )}
        </Section>
      )}

      {/* ══ DASHBOARD / KPIs ══ */}
      {isTeaser && !dashboard.north_star_metric && <PaywallLock title="Dashboard & KPIs" onUpgrade={handleUpgrade} />}
      {dashboard.north_star_metric && (
        <Section id="sec-kpis" title="Dashboard & KPIs">
          <div className="bg-surface border border-border rounded-xl p-6 text-center mb-3">
            <p className="text-[10px] text-text2 uppercase tracking-wider">North Star Metric</p>
            <p className="text-lg font-bold text-accent2 mt-1">{dashboard.north_star_metric}</p>
            {dashboard.north_star_target && <p className="text-xs text-text2 mt-1">Target: {dashboard.north_star_target}</p>}
          </div>
          {(dashboard.primary_kpis?.length || dashboard.alerts?.length) && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {dashboard.primary_kpis?.map((kpi, i) => (
                <div key={i} className="bg-surface border border-border rounded-xl p-4">
                  <p className="text-[10px] text-success font-bold uppercase">Primary KPI</p>
                  <p className="text-sm font-semibold mt-1">{kpi}</p>
                </div>
              ))}
            </div>
          )}
          {dashboard.alerts && dashboard.alerts.length > 0 && (
            <div className="bg-surface border border-border rounded-xl p-5 mt-3">
              <p className="font-semibold text-sm mb-3">Alert Thresholds</p>
              {dashboard.alerts.map((a, i) => (
                <div key={i} className="flex items-start gap-2 py-1.5 border-b border-border/50 last:border-0 text-sm">
                  <span className="w-2 h-2 rounded-full bg-danger shrink-0 mt-1.5" />
                  <span><strong>{a.metric}</strong>: {a.threshold} &rarr; <span className="text-accent2">{a.action}</span></span>
                </div>
              ))}
            </div>
          )}
        </Section>
      )}
    </div>
  );
}
