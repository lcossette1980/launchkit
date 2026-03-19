import { Navigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

/* ── Mockup frame component ─────────────────────────────── */
function AppMockup({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`rounded-xl border border-border/60 bg-surface overflow-hidden shadow-2xl shadow-accent/5 ${className}`}>
      {/* Browser chrome */}
      <div className="flex items-center gap-1.5 px-4 py-2.5 bg-surface2 border-b border-border/60">
        <div className="w-2.5 h-2.5 rounded-full bg-red-500/60" />
        <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/60" />
        <div className="w-2.5 h-2.5 rounded-full bg-green-500/60" />
        <div className="ml-3 flex-1 bg-bg/60 rounded-md h-5 flex items-center px-2">
          <span className="text-[10px] text-text2/50">launchkit.dev</span>
        </div>
      </div>
      <div className="p-5">{children}</div>
    </div>
  );
}

/* ── Score pill used in mockups ──────────────────────────── */
function ScorePill({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="text-center">
      <div className={`text-xl font-bold ${color}`}>{value}</div>
      <div className="text-[10px] uppercase tracking-wider text-text2 mt-0.5">{label}</div>
    </div>
  );
}

/* ── Main landing page ──────────────────────────────────── */
export default function LandingPage() {
  const { user, loading } = useAuth();

  if (loading) return null;
  if (user) return <Navigate to="/dashboard" replace />;

  return (
    <div className="min-h-screen bg-bg">
      {/* ═══ Nav ═══ */}
      <nav className="border-b border-border/50 bg-bg/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-5 flex items-center justify-between h-14">
          <span className="text-lg font-bold tracking-tight">
            <span className="text-accent2">Launch</span>Kit
          </span>
          <div className="flex items-center gap-5">
            <a href="#how-it-works" className="text-sm text-text2 hover:text-text transition-colors hidden sm:block">How It Works</a>
            <a href="#what-you-get" className="text-sm text-text2 hover:text-text transition-colors hidden sm:block">Features</a>
            <Link to="/examples" className="text-sm text-text2 hover:text-text transition-colors hidden sm:block">Examples</Link>
            <Link to="/pricing" className="text-sm text-text2 hover:text-text transition-colors">Pricing</Link>
            <Link to="/login" className="px-4 py-1.5 bg-accent hover:bg-accent2 text-white text-sm font-semibold rounded-lg transition-colors">
              Sign In
            </Link>
          </div>
        </div>
      </nav>

      {/* ═══ Hero ═══ */}
      <section className="max-w-5xl mx-auto px-5 pt-20 pb-6">
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-accent2 text-sm font-medium tracking-wide uppercase mb-4">From URL to GTM strategy in 10 minutes</p>
          <h1 className="text-4xl md:text-[3.2rem] font-bold tracking-tight leading-[1.15] mb-5">
            Crawl your site.<br />Benchmark competitors.<br />Ship a real plan.
          </h1>
          <p className="text-text2 text-lg max-w-2xl mx-auto mb-8 leading-relaxed">
            Paste your URL. Get a page-by-page audit, 5+ competitor deep-dives, a complete copy kit, email templates, and a 30/60/90 day roadmap — evidence-backed and ready to execute.
          </p>
          <p className="text-text2/70 text-sm max-w-lg mx-auto mb-8">
            Analyzes every page on your site. Researches your market. Produces 10 sections of actionable strategy you can paste into Notion and start executing today.
          </p>
          <div className="flex gap-3 justify-center mb-4">
            <Link to="/login" className="px-7 py-3 bg-accent hover:bg-accent2 text-white font-semibold rounded-lg transition-colors text-[15px]">
              Get Your Free Playbook
            </Link>
            <a href="#how-it-works" className="px-7 py-3 border border-border text-text2 hover:border-accent/50 hover:text-text font-medium rounded-lg transition-colors text-[15px]">
              See How It Works
            </a>
          </div>
          <p className="text-text2/60 text-xs">No credit card required. First analysis is free.</p>
        </div>
      </section>

      {/* ═══ Hero Mockup — Scores ═══ */}
      <section className="max-w-4xl mx-auto px-5 pt-8 pb-20">
        <AppMockup>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[10px] text-text2 uppercase tracking-wider">← Dashboard</p>
                <p className="text-lg font-bold mt-0.5">AI Consulting</p>
              </div>
              <div className="flex gap-2">
                <span className="text-[10px] px-2 py-1 border border-border rounded text-text2">HTML Report</span>
                <span className="text-[10px] px-2 py-1 border border-border rounded text-text2">JSON</span>
              </div>
            </div>
            <div className="flex gap-2 flex-wrap">
              {["Summary", "Scores", "Pages", "Market", "Competitors", "Strategy", "Roadmap", "Copy Kit", "Outreach", "KPIs"].map((s) => (
                <span key={s} className={`text-[10px] px-2.5 py-1 rounded-md border ${s === "Scores" ? "border-accent bg-accent/10 text-accent2" : "border-border text-text2"}`}>{s}</span>
              ))}
            </div>
            <div>
              <p className="text-accent2 text-[11px] font-semibold uppercase tracking-wider mb-3">Website Scores</p>
              <div className="grid grid-cols-5 gap-3">
                <ScorePill label="Clarity" value={73} color="text-green-400" />
                <ScorePill label="Audience" value={69} color="text-yellow-400" />
                <ScorePill label="Conversion" value={51} color="text-red-400" />
                <ScorePill label="SEO" value={58} color="text-yellow-400" />
                <ScorePill label="UX" value={64} color="text-yellow-400" />
              </div>
            </div>
            <div className="bg-surface2 rounded-lg p-3 border border-border/50">
              <p className="text-green-400 text-[10px] font-semibold uppercase mb-2">Strengths</p>
              <div className="space-y-1.5">
                <div className="flex gap-2 items-start text-[11px] text-text2">
                  <span className="text-green-400 mt-px">+</span>
                  <span>Clear professional identity and value proposition in H1 text</span>
                </div>
                <div className="flex gap-2 items-start text-[11px] text-text2">
                  <span className="text-green-400 mt-px">+</span>
                  <span>Strong credibility signals with specific performance metrics</span>
                </div>
              </div>
            </div>
          </div>
        </AppMockup>
      </section>

      {/* ═══ How It Works ═══ */}
      <section id="how-it-works" className="bg-surface/50 border-y border-border/30 py-20">
        <div className="max-w-5xl mx-auto px-5">
          <div className="text-center mb-14">
            <p className="text-accent2 text-sm font-medium uppercase tracking-wide mb-2">How it works</p>
            <h2 className="text-3xl font-bold">From URL to playbook in three steps</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                step: "01",
                title: "Enter your URL",
                desc: "Paste your website URL, add your brand name and target audience. That's it — takes 30 seconds.",
              },
              {
                step: "02",
                title: "AI analyzes everything",
                desc: "9 specialized AI agents crawl your site, research your market, analyze competitors, and generate strategy. ~8 minutes.",
              },
              {
                step: "03",
                title: "Get your playbook",
                desc: "Receive a comprehensive GTM playbook with scores, page-by-page fixes, copy kit, email templates, and a 30/60/90 roadmap.",
              },
            ].map((s) => (
              <div key={s.step} className="relative">
                <span className="text-5xl font-bold text-accent/10 absolute -top-3 -left-1">{s.step}</span>
                <div className="relative pt-8">
                  <h3 className="text-lg font-semibold mb-2">{s.title}</h3>
                  <p className="text-text2 text-sm leading-relaxed">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ What You Get ═══ */}
      <section id="what-you-get" className="py-20">
        <div className="max-w-5xl mx-auto px-5">
          <div className="text-center mb-14">
            <p className="text-accent2 text-sm font-medium uppercase tracking-wide mb-2">What you get</p>
            <h2 className="text-3xl font-bold">Everything you need to launch and grow</h2>
            <p className="text-text2 mt-3 max-w-xl mx-auto">Each analysis produces 10 detailed sections. Not generic advice — specific, actionable recommendations tailored to your product.</p>
          </div>

          {/* Feature: Website Audit + Roadmap (with mockups) */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
            {/* Website Audit */}
            <div>
              <h3 className="text-xl font-semibold mb-2">Page-by-page website audit</h3>
              <p className="text-text2 text-sm leading-relaxed mb-5">
                Every page on your site gets scored on clarity, audience fit, conversion, SEO, and UX. Each score comes with specific strengths, weaknesses, and fix-this-here recommendations.
              </p>
              <AppMockup>
                <div className="space-y-2">
                  <p className="text-[10px] text-accent2 uppercase font-semibold tracking-wider">Page Analysis — /consulting</p>
                  <div className="space-y-1.5">
                    {[
                      { label: "Clarity", val: 75, w: "75%" },
                      { label: "Audience Fit", val: 80, w: "80%" },
                      { label: "Conversion", val: 65, w: "65%" },
                      { label: "SEO", val: 60, w: "60%" },
                      { label: "UX", val: 70, w: "70%" },
                    ].map((s) => (
                      <div key={s.label} className="flex items-center gap-2 text-[11px]">
                        <span className="text-text2 w-20">{s.label}</span>
                        <div className="flex-1 h-1.5 bg-bg rounded-full overflow-hidden">
                          <div className="h-full bg-accent2 rounded-full" style={{ width: s.w }} />
                        </div>
                        <span className="text-text font-semibold w-6 text-right">{s.val}</span>
                      </div>
                    ))}
                  </div>
                  <div className="mt-3 pt-2 border-t border-border/30 text-[10px] text-accent2">
                    <span className="font-semibold">RECOMMENDATION:</span>
                    <span className="text-text2 ml-1">Rewrite the main headline to explicitly state the key benefit for CTOs...</span>
                  </div>
                </div>
              </AppMockup>
            </div>

            {/* Roadmap */}
            <div>
              <h3 className="text-xl font-semibold mb-2">30/60/90 day roadmap</h3>
              <p className="text-text2 text-sm leading-relaxed mb-5">
                Not just what to do — when to do it. A phased implementation plan that prioritizes quick wins first, then builds momentum over 90 days.
              </p>
              <AppMockup>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { phase: "30 Days", items: ["Update website headline and hero", "Add lead capture form", "Start LinkedIn posting 2x/week", "Create pricing page"] },
                    { phase: "60 Days", items: ["Publish first case study", "Run LinkedIn ad campaign", "Create email nurture sequence", "Launch lead magnet"] },
                    { phase: "90 Days", items: ["Host webinar for CTOs", "Secure podcast appearances", "Gather client testimonials", "Review and optimize campaigns"] },
                  ].map((p) => (
                    <div key={p.phase} className="bg-surface2 rounded-lg p-2.5 border border-border/30">
                      <p className="text-accent2 text-[10px] font-bold mb-2">{p.phase}</p>
                      <ul className="space-y-1">
                        {p.items.map((item, i) => (
                          <li key={i} className="text-[10px] text-text2 leading-snug flex gap-1">
                            <span className="text-text2/40">-</span> {item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </AppMockup>
            </div>
          </div>

          {/* Feature grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {[
              {
                title: "Competitor deep-dives",
                desc: "5+ competitors analyzed: their value proposition, target audience, pricing model, differentiators, strengths, and weaknesses. Know exactly where you stand.",
              },
              {
                title: "Ready-to-use copy kit",
                desc: "5 headlines with subheadlines and CTAs. Value propositions. A complete landing page blueprint with problem, solution, benefits, social proof, and FAQ sections.",
              },
              {
                title: "Email & LinkedIn templates",
                desc: "Welcome email, follow-up, and re-engagement templates. LinkedIn connection request, follow-up, and value-share messages. Copy, paste, send.",
              },
              {
                title: "Ad copy for 3 platforms",
                desc: "Google Search, Facebook, and LinkedIn ad copy with headlines, descriptions, and CTAs. Ready to launch campaigns the same day.",
              },
              {
                title: "Market research & keywords",
                desc: "Target audience definition, competitive landscape overview, 10 keyword opportunities, and 10 content topics to write about. SEO strategy included.",
              },
              {
                title: "KPI dashboard spec",
                desc: "North star metric, primary and secondary KPIs, daily/weekly/monthly tracking cadence, and alert thresholds. Know what to measure from day one.",
              },
            ].map((f, i) => (
              <div key={i} className="bg-surface border border-border/50 rounded-xl p-5 hover:border-border transition-colors">
                <h3 className="font-semibold text-[15px] mb-1.5">{f.title}</h3>
                <p className="text-sm text-text2 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ Social proof placeholder ═══ */}
      <section className="bg-surface/50 border-y border-border/30 py-14">
        <div className="max-w-4xl mx-auto px-5 text-center">
          <p className="text-text2 text-sm italic leading-relaxed max-w-2xl mx-auto">
            "I spent weeks trying to figure out my GTM strategy. LaunchKit gave me a complete playbook in 8 minutes. The page-by-page analysis alone was worth it — I found conversion issues I'd been blind to."
          </p>
          <p className="text-text2/50 text-xs mt-4">— Early beta user</p>
        </div>
      </section>

      {/* ═══ Pricing preview ═══ */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-5">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold mb-2">Simple pricing</h2>
            <p className="text-text2">Start free. Upgrade when you need more.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { name: "Free", price: "$0", sub: "forever", features: ["1 analysis/month", "Executive summary", "Website scores", "Top 3 priorities"], featured: false },
              { name: "Pro", price: "$29", sub: "/month", features: ["5 analyses/month", "Full page-by-page breakdown", "Copy kit + email templates", "30/60/90 roadmap", "Competitor deep-dives", "HTML/JSON export"], featured: true },
              { name: "Agency", price: "$79", sub: "/month", features: ["25 analyses/month", "Everything in Pro", "Unlimited brands", "API access"], featured: false },
            ].map((p) => (
              <div key={p.name} className={`border rounded-xl p-6 text-center ${p.featured ? "border-accent bg-accent/[0.03] ring-1 ring-accent/20" : "border-border bg-surface"}`}>
                <h3 className="font-bold mb-1">{p.name}</h3>
                <div className="mb-3">
                  <span className="text-3xl font-bold text-accent2">{p.price}</span>
                  <span className="text-sm text-text2">{p.sub}</span>
                </div>
                <ul className="text-left text-sm text-text2 space-y-1.5 mb-5">
                  {p.features.map((f, i) => (
                    <li key={i} className="flex gap-2 items-start">
                      <span className="text-accent2 mt-0.5 text-xs">&#10003;</span>
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>
                <Link
                  to="/login"
                  className={`block w-full py-2.5 text-sm font-semibold rounded-lg text-center transition-colors ${
                    p.featured ? "bg-accent hover:bg-accent2 text-white" : "border border-border text-text2 hover:border-accent hover:text-accent2"
                  }`}
                >
                  {p.featured ? "Get Started" : "Start Free"}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ Final CTA ═══ */}
      <section className="py-20">
        <div className="max-w-2xl mx-auto px-5 text-center">
          <h2 className="text-3xl font-bold mb-3">Ship a credible GTM plan in under an hour</h2>
          <p className="text-text2 mb-8 leading-relaxed">
            Your first analysis is free. No credit card. No sales calls. Paste your URL, get your playbook, start executing.
          </p>
          <Link to="/login" className="px-8 py-3.5 bg-accent hover:bg-accent2 text-white font-semibold rounded-lg transition-colors text-[15px] inline-block">
            Get Your Free Playbook
          </Link>
        </div>
      </section>

      {/* ═══ Footer ═══ */}
      <footer className="border-t border-border/30 py-8">
        <div className="max-w-6xl mx-auto px-5 flex items-center justify-between">
          <span className="text-sm text-text2/50">
            <span className="text-accent2/50 font-semibold">Launch</span>Kit
          </span>
          <div className="flex gap-5 text-xs text-text2/40">
            <Link to="/pricing" className="hover:text-text2 transition-colors">Pricing</Link>
            <Link to="/login" className="hover:text-text2 transition-colors">Sign In</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
