import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getSharedReport } from "../api/analyses";
import type { FullReport, Scores } from "../types/api";
import SEO from "../components/SEO";

/* Reuse score helpers */
function scoreColor(v: number) {
  if (v >= 75) return "text-success";
  if (v >= 50) return "text-warning";
  return "text-danger";
}

export default function SharedReportPage() {
  const { token } = useParams<{ token: string }>();
  const [data, setData] = useState<{
    brand: string;
    site_url: string;
    completed_at: string | null;
    results: FullReport;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    getSharedReport(token)
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : "Report not found"));
  }, [token]);

  if (error) {
    return (
      <div className="min-h-screen bg-bg flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-2">Report Not Found</h1>
          <p className="text-text2 mb-6">This share link may have expired or been revoked.</p>
          <Link to="/" className="px-5 py-2.5 bg-accent text-white font-semibold rounded-lg">
            Get Your Own GTM Playbook
          </Link>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-bg flex items-center justify-center">
        <p className="text-text2 animate-pulse">Loading shared report...</p>
      </div>
    );
  }

  const r = data.results;
  const exec = r.executive_summary ?? {};
  const web = r.website_analysis ?? {};
  const scores: Scores = web.overall_scores ?? {} as Scores;
  const strategy = r.gtm_strategy ?? {};
  const roadmap = strategy.implementation_roadmap ?? {};
  const crawlFailed = web.crawl_failed === true || web.overall_scores === null;
  const scoresAreEmpty = !web.overall_scores || Object.values(web.overall_scores).every(v => v === 0);

  return (
    <div className="min-h-screen bg-bg">
      <SEO
        title={data.brand ? `${data.brand} — GTM Playbook` : "Shared GTM Playbook"}
        description={exec.overview ? exec.overview.slice(0, 160) : "Complete GTM playbook with page-by-page audit, competitor analysis, copy kit, and roadmap."}
        path={`/share/${token}`}
      />
      {/* Shared report nav */}
      <nav className="border-b border-border bg-surface/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-5 flex items-center justify-between h-12">
          <div className="flex items-center gap-4">
            <Link to="/" className="text-sm font-bold">
              <span className="text-accent2">VC</span>LaunchKit
            </Link>
            <Link to="/examples" className="text-xs text-text2 hover:text-accent2 transition-colors">
              &larr; All Examples
            </Link>
          </div>
          <Link
            to="/login"
            className="px-4 py-1.5 bg-accent hover:bg-accent2 text-white text-xs font-semibold rounded-lg transition-colors"
          >
            Get Your Own Playbook
          </Link>
        </div>
      </nav>

      <div className="max-w-5xl mx-auto px-5 py-8">
        {/* Header */}
        <div className="mb-6">
          <p className="text-xs text-text2 mb-1">Shared GTM Playbook</p>
          <h1 className="text-2xl font-bold">{data.brand}</h1>
          <p className="text-sm text-text2 mt-1">{data.site_url}</p>
          {data.completed_at && (
            <p className="text-xs text-text2/50 mt-1">
              Generated {new Date(data.completed_at).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}
            </p>
          )}
        </div>

        {/* Preview notice */}
        <div className="mb-6 bg-accent/5 border border-accent/20 rounded-xl p-4 flex items-start gap-3">
          <span className="text-accent2 text-sm mt-0.5">&#9432;</span>
          <div>
            <p className="text-sm font-medium mb-1">This is a preview report</p>
            <p className="text-xs text-text2 leading-relaxed">
              You're seeing the executive summary, scores, and top priorities. The full report includes
              page-by-page analysis, competitor deep-dives, copy kit, email templates, ad copy,
              30/60/90 roadmap, and KPI dashboard.{" "}
              <Link to="/login" className="text-accent2 hover:underline">Sign up free</Link> to generate your own complete playbook.
            </p>
          </div>
        </div>

        {/* Executive Summary */}
        {crawlFailed && (
          <section className="mb-6">
            <div className="bg-warning/10 border border-warning/40 rounded-xl p-5">
              <div className="flex gap-2.5 items-start">
                <span className="text-warning text-lg shrink-0">&#9888;</span>
                <div>
                  <p className="font-semibold text-sm text-warning mb-1">Website Crawl Failed</p>
                  <p className="text-sm leading-relaxed">
                    We were unable to crawl this website. The site may be down, blocking automated access, or the URL may be incorrect.
                    Website-specific scores are unavailable. The remaining analysis is based on publicly available information.
                  </p>
                  {web.crawl_errors && web.crawl_errors.length > 0 && (
                    <ul className="mt-2 text-xs text-text2 space-y-1 list-disc pl-4">
                      {web.crawl_errors.map((err: string, i: number) => <li key={i}>{err}</li>)}
                    </ul>
                  )}
                </div>
              </div>
            </div>
          </section>
        )}
        {exec.overview && (
          <section className="mb-6">
            <h2 className="text-accent2 text-xs font-semibold uppercase tracking-wider mb-3">Executive Summary</h2>
            <div className="bg-surface border border-border rounded-xl p-5">
              <p className="text-sm leading-relaxed">{exec.overview}</p>
            </div>
          </section>
        )}

        {/* Scores */}
        {(crawlFailed || scoresAreEmpty) && (
          <section className="mb-6">
            <h2 className="text-accent2 text-xs font-semibold uppercase tracking-wider mb-3">Website Scores</h2>
            <div className="bg-warning/10 border border-warning/40 rounded-xl p-5">
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
          </section>
        )}
        {!crawlFailed && !scoresAreEmpty && Object.keys(scores).length > 0 && (
          <section className="mb-6">
            <h2 className="text-accent2 text-xs font-semibold uppercase tracking-wider mb-3">Website Scores</h2>
            <div className="grid grid-cols-5 gap-3">
              {Object.entries(scores).map(([k, v]) => (
                <div key={k} className="bg-surface border border-border rounded-xl p-4 text-center">
                  <div className={`text-2xl font-bold ${scoreColor(v as number)}`}>{v as number}</div>
                  <div className="text-[10px] uppercase tracking-wider text-text2 mt-1">
                    {k.replace(/_/g, " ")}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Top Priorities */}
        {exec.top_priorities?.length ? (
          <section className="mb-6">
            <h2 className="text-accent2 text-xs font-semibold uppercase tracking-wider mb-3">Top Priorities</h2>
            <div className="bg-surface border border-border rounded-xl p-5 space-y-3">
              {exec.top_priorities.map((p: string, i: number) => (
                <div key={i} className="flex gap-3 items-start text-sm">
                  <span className="w-6 h-6 rounded-full bg-accent/15 text-accent2 text-xs font-bold flex items-center justify-center flex-shrink-0">
                    {i + 1}
                  </span>
                  <span className="text-text2">{p}</span>
                </div>
              ))}
            </div>
          </section>
        ) : null}

        {/* 30/60/90 Roadmap */}
        {roadmap["30_day"]?.length ? (
          <section className="mb-6">
            <h2 className="text-accent2 text-xs font-semibold uppercase tracking-wider mb-3">Implementation Roadmap</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {(["30_day", "60_day", "90_day"] as const).map((phase) => {
                const items = roadmap[phase] ?? [];
                if (!items.length) return null;
                const label = phase.replace("_", " ").replace("day", "Days");
                return (
                  <div key={phase} className="bg-surface border border-border rounded-xl p-4">
                    <h3 className="text-accent2 text-xs font-bold uppercase mb-2">{label}</h3>
                    <ul className="text-xs text-text2 space-y-1.5">
                      {items.map((item: string, i: number) => (
                        <li key={i} className="flex gap-1.5">
                          <span className="text-text2/40">-</span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                );
              })}
            </div>
          </section>
        ) : null}

        {/* Locked sections preview */}
        <section className="mb-8">
          <h2 className="text-accent2 text-xs font-semibold uppercase tracking-wider mb-4">Also included in full report</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[
              { title: "Page-by-Page Analysis", desc: "Every page scored on clarity, audience fit, conversion, SEO, and UX with specific fix-this-here recommendations" },
              { title: "Competitor Deep-Dives", desc: "5+ competitors analyzed: value proposition, target audience, pricing, differentiators, strengths, and weaknesses" },
              { title: "Complete Copy Kit", desc: "5 headlines with subheadlines and CTAs, value propositions, and a full landing page blueprint" },
              { title: "Email & LinkedIn Templates", desc: "Welcome, follow-up, and re-engagement emails. LinkedIn connection, follow-up, and value-share messages" },
              { title: "Ad Copy (3 Platforms)", desc: "Google Search, Facebook, and LinkedIn ad copy with headlines, descriptions, and CTAs" },
              { title: "Market Research", desc: "Target audience definition, competitive landscape, 10 keyword opportunities, and 10 content topics" },
              { title: "KPI Dashboard", desc: "North star metric, primary/secondary KPIs, daily/weekly/monthly tracking cadence, and alert thresholds" },
              { title: "HTML & JSON Export", desc: "Download the full report as a branded HTML document or structured JSON for integration with your tools" },
            ].map((s) => (
              <div key={s.title} className="bg-surface border border-border/50 rounded-lg p-4 opacity-60">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-text2/40 text-xs">&#128274;</span>
                  <h3 className="text-sm font-medium text-text2">{s.title}</h3>
                </div>
                <p className="text-xs text-text2/60 leading-relaxed">{s.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* CTA Banner */}
        <div className="mt-6 bg-gradient-to-r from-accent/10 to-accent2/10 border border-accent/20 rounded-xl p-8 text-center">
          <h2 className="text-xl font-bold mb-2">Want the full playbook?</h2>
          <p className="text-text2 text-sm mb-5 max-w-md mx-auto">
            Get all sections including page-by-page analysis, competitor intel, copy kit, email templates, ad copy, and downloadable reports.
          </p>
          <Link
            to="/login"
            className="px-6 py-3 bg-accent hover:bg-accent2 text-white font-semibold rounded-lg transition-colors inline-block"
          >
            Get Started Free
          </Link>
        </div>

        {/* Watermark footer */}
        <div className="mt-8 text-center text-xs text-text2/40 pb-8">
          Generated by <span className="text-accent2/50 font-semibold">Launch</span><span className="text-text2/50">Kit</span> &mdash; AI-powered GTM playbooks for builders
        </div>
      </div>
    </div>
  );
}
