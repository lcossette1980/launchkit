import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import SEO from "../components/SEO";
import PublicNav from "../components/PublicNav";

interface BlogPost {
  slug: string;
  title: string;
  excerpt: string;
  date: string;
  readTime: string;
  tags: string[];
}

const POSTS: BlogPost[] = [
  {
    slug: "how-vclaunchkit-works",
    title: "How VCLaunchKit works: From URL to GTM playbook in 10 minutes",
    excerpt:
      "Most solo developers and small teams know how to build products but struggle with go-to-market strategy. We built VCLaunchKit to fix that. Here's exactly what happens when you paste your URL.",
    date: "March 19, 2026",
    readTime: "5 min read",
    tags: ["Product", "How It Works"],
  },
  {
    slug: "why-vibecoders-need-gtm",
    title: "Why vibecoders need a GTM strategy (and how AI makes it painless)",
    excerpt:
      "You can build a product in a weekend with AI. But shipping it to the right audience with the right messaging? That still takes weeks of research — unless you automate it.",
    date: "March 19, 2026",
    readTime: "4 min read",
    tags: ["Strategy", "Vibecoders"],
  },
  {
    slug: "competitor-analysis-solo-dev",
    title: "How to run a competitor analysis as a solo developer (without spending $5K on consultants)",
    excerpt:
      "Enterprise companies pay McKinsey for competitor research. Solo developers can now get the same depth of analysis — value propositions, pricing models, differentiators — from AI agents that do the work in minutes.",
    date: "March 19, 2026",
    readTime: "6 min read",
    tags: ["Competitor Analysis", "Solo Developers"],
  },
];

/* ── Post content components ─────────────────────────────── */

function HowItWorks() {
  return (
    <div className="space-y-6 text-[15px] leading-relaxed text-text2">
      <p>
        Most solo developers and small teams build incredible products — but when it comes to
        go-to-market strategy, they're stuck Googling "how to launch a SaaS" and piecing
        together generic advice from blog posts written for Series B companies with 50-person
        marketing teams.
      </p>
      <p>We built VCLaunchKit to solve this. Here's exactly what happens when you paste your URL.</p>

      <h3 className="text-xl font-semibold text-text mt-10 mb-3">Step 1: The quick scan (3 minutes)</h3>
      <p>
        When you submit a URL, three specialized AI agents immediately go to work. The <strong className="text-text">Planner</strong> determines
        which pages to analyze and what competitor queries to run. The <strong className="text-text">Crawler</strong> follows your sitemap and
        internal links to discover every page on your site. Then the <strong className="text-text">Page Analyzer</strong> scores each page on
        five dimensions: clarity, audience fit, conversion potential, SEO, and UX.
      </p>
      <p>
        Within 3 minutes, you see your initial scores while the deep analysis continues in the background.
        This "quick scan" approach means you're never staring at a loading screen wondering if something broke.
      </p>

      <h3 className="text-xl font-semibold text-text mt-10 mb-3">Step 2: Market research and competitor deep-dives</h3>
      <p>
        The <strong className="text-text">Market Researcher</strong> agent identifies trends in your space, defines your target audience
        with precision, maps the competitive landscape, and surfaces 10 keyword opportunities and 10 content topics
        you should be writing about. This isn't surface-level — it uses SerpAPI to research actual search results
        and market data.
      </p>
      <p>
        Then the <strong className="text-text">Competitor Analyzer</strong> takes the top 5 competitors and produces a complete profile
        for each: their value proposition, target audience, pricing model, key differentiators, strengths,
        weaknesses, and content strategy. This is the kind of analysis a marketing consultant charges $5,000+ for.
      </p>

      <h3 className="text-xl font-semibold text-text mt-10 mb-3">Step 3: Strategy, experiments, and copy</h3>
      <p>
        The <strong className="text-text">Strategist</strong> agent generates your positioning (3 options), recommends primary and secondary
        channels, outlines a content strategy, identifies partnership opportunities, and gives specific
        pricing recommendations. All based on your actual site content, market data, and competitor gaps — not templates.
      </p>
      <p>
        The <strong className="text-text">Experimenter</strong> designs 15+ growth experiments ranked by ICE score (Impact, Confidence, Effort).
        Each experiment has a hypothesis, success metric, and implementation details. The highest-ICE experiments
        are your quick wins.
      </p>
      <p>
        Finally, the <strong className="text-text">Copywriter</strong> generates 5 headlines with subheadlines and CTAs, 3 value propositions,
        3 email templates (welcome, follow-up, re-engagement), LinkedIn messages, ad copy for Google/Facebook/LinkedIn,
        and a complete landing page blueprint with problem/solution/benefits/social proof/FAQ sections.
      </p>

      <h3 className="text-xl font-semibold text-text mt-10 mb-3">What you get: a 10-section GTM playbook</h3>
      <p>
        The <strong className="text-text">Synthesizer</strong> assembles everything into a comprehensive report with a 30/60/90 day implementation
        roadmap. Not "maybe consider posting on social media someday" — specific actions like "Update website headline
        to state the key benefit for your target audience" and "Launch LinkedIn content campaign targeting CTOs with
        8 posts per month."
      </p>
      <p>
        Export as HTML, PDF, or JSON. Share with a public link. Re-run monthly to track score improvements.
        Your first analysis is free.
      </p>
    </div>
  );
}

function WhyVibecodersNeedGTM() {
  return (
    <div className="space-y-6 text-[15px] leading-relaxed text-text2">
      <p>
        The vibecoder revolution changed how products get built. With AI-assisted development, a solo developer
        can ship a production-ready SaaS in a weekend. The technical barriers to building are lower than
        they've ever been.
      </p>
      <p>
        But here's what nobody talks about: <strong className="text-text">building the product was the easy part.</strong>
      </p>

      <h3 className="text-xl font-semibold text-text mt-10 mb-3">The GTM gap</h3>
      <p>
        Most vibecoders are engineers first. They think in systems, APIs, and deployment pipelines. But
        go-to-market strategy requires a completely different skillset: positioning, messaging, audience
        segmentation, competitive analysis, channel selection, and conversion optimization.
      </p>
      <p>
        The typical vibecoder GTM "strategy" looks like this: ship it, post on Twitter, submit to Product Hunt,
        and hope. When that doesn't work, they Google "how to market a SaaS" and find advice designed for
        companies with $50K marketing budgets and dedicated teams.
      </p>

      <h3 className="text-xl font-semibold text-text mt-10 mb-3">What a real GTM strategy looks like</h3>
      <p>A proper go-to-market strategy answers these questions:</p>
      <ul className="list-disc pl-6 space-y-2 mt-4">
        <li><strong className="text-text">Positioning:</strong> What makes your product different from the 5 competitors in your space?</li>
        <li><strong className="text-text">Messaging:</strong> What specific words resonate with your target audience's pain points?</li>
        <li><strong className="text-text">Channels:</strong> Where does your audience actually spend time? (Hint: it's probably not Facebook.)</li>
        <li><strong className="text-text">Conversion:</strong> What's stopping visitors from signing up on your current site?</li>
        <li><strong className="text-text">Roadmap:</strong> What should you do this week vs. this month vs. next quarter?</li>
      </ul>

      <h3 className="text-xl font-semibold text-text mt-10 mb-3">Why AI changes the equation</h3>
      <p>
        Traditionally, getting answers to these questions required either weeks of manual research or
        hiring a marketing consultant at $150-300/hour. A typical engagement runs $5,000-15,000 and
        takes 4-6 weeks.
      </p>
      <p>
        AI agents can now do the same work in minutes. Not because AI is smarter than a seasoned marketer,
        but because 80% of GTM research is systematic: crawling pages, analyzing copy, benchmarking competitors,
        and identifying patterns. AI excels at exactly this kind of structured analysis.
      </p>
      <p>
        The remaining 20% — creative judgment, market intuition, brand voice — that's still on you. But
        having the research done means you're making creative decisions based on data instead of gut feelings.
      </p>

      <h3 className="text-xl font-semibold text-text mt-10 mb-3">The vibecoder advantage</h3>
      <p>
        Here's the irony: vibecoders are actually <em>better positioned</em> to execute on GTM strategies than
        traditional marketers. Why? Because they can implement changes immediately. A marketer who identifies
        a conversion issue needs to file a ticket with engineering. A vibecoder just fixes it.
      </p>
      <p>
        The only missing piece was the analysis itself. That's what VCLaunchKit provides: the research,
        the strategy, and the specific recommendations — so you can spend your time executing instead of researching.
      </p>
    </div>
  );
}

function CompetitorAnalysis() {
  return (
    <div className="space-y-6 text-[15px] leading-relaxed text-text2">
      <p>
        When enterprise companies need to understand their competitive landscape, they hire firms like
        McKinsey, Bain, or specialized agencies. These engagements typically cost $10,000-50,000 and
        take 4-8 weeks. The deliverable? A 50-page PDF with market maps, competitor profiles, and
        strategic recommendations.
      </p>
      <p>
        As a solo developer, you need the same intelligence — but you have neither the budget nor the time.
        Here's how to get it anyway.
      </p>

      <h3 className="text-xl font-semibold text-text mt-10 mb-3">What a real competitor analysis covers</h3>
      <p>A useful competitor analysis goes far beyond "here are 5 companies that do something similar." For each competitor, you need:</p>
      <ul className="list-disc pl-6 space-y-2 mt-4">
        <li><strong className="text-text">Value proposition:</strong> What exactly do they promise? How do they frame the problem they solve?</li>
        <li><strong className="text-text">Target audience:</strong> Who are they selling to? Is it the same audience as yours, or adjacent?</li>
        <li><strong className="text-text">Pricing model:</strong> Freemium? Usage-based? Per-seat? What can you learn from their pricing choices?</li>
        <li><strong className="text-text">Key differentiators:</strong> What do they claim makes them unique? Is it real or marketing fluff?</li>
        <li><strong className="text-text">Strengths:</strong> What are they genuinely good at? Where would you lose in a head-to-head comparison?</li>
        <li><strong className="text-text">Weaknesses:</strong> Where are the gaps? What complaints do their users have? What's missing?</li>
        <li><strong className="text-text">Content strategy:</strong> How do they attract customers? Blog? Community? Paid ads? Partnerships?</li>
      </ul>

      <h3 className="text-xl font-semibold text-text mt-10 mb-3">The manual approach (and why it breaks down)</h3>
      <p>
        The traditional way to do this is to spend a Saturday afternoon visiting each competitor's website,
        reading their landing pages, checking their pricing, and taking notes in a spreadsheet. The problems:
      </p>
      <ul className="list-disc pl-6 space-y-2 mt-4">
        <li>You don't know who your real competitors are (the ones you find on Google might not be the right ones)</li>
        <li>You miss the non-obvious competitors — the adjacent products that could eat your lunch</li>
        <li>Your analysis is biased by what you notice vs. what actually matters</li>
        <li>It takes 4-6 hours for a thorough job, and you'll probably never update it</li>
        <li>You have no framework for turning insights into action</li>
      </ul>

      <h3 className="text-xl font-semibold text-text mt-10 mb-3">The AI approach</h3>
      <p>
        VCLaunchKit's competitor analysis works differently. First, the Market Researcher agent searches
        for competitors based on your <em>product category and target audience</em> — not just your brand name.
        This surfaces competitors you might not have known about.
      </p>
      <p>
        Then for each of the top 5 competitors, an AI agent visits their site, reads their content,
        and produces a structured profile covering all seven dimensions above. The output isn't a wall of
        text — it's organized into strengths, weaknesses, differentiators, and content strategy sections
        that you can act on immediately.
      </p>

      <h3 className="text-xl font-semibold text-text mt-10 mb-3">Turning analysis into action</h3>
      <p>
        The most valuable part isn't knowing what competitors do — it's knowing what to do differently.
        VCLaunchKit's strategy agent takes the competitor analysis and generates specific positioning
        recommendations: where you should compete head-on, where you should differentiate, and where
        you should avoid competing entirely.
      </p>
      <p>
        For example, if every competitor in your space has opaque pricing, the strategy might recommend
        transparent pricing as a differentiator. If competitors are strong on content but weak on
        community, it might recommend building a community as your primary channel.
      </p>
      <p>
        The result: competitor intelligence that would cost $5K+ from a consultant, delivered in under
        10 minutes, specific to your product and audience.
      </p>
    </div>
  );
}

const POST_COMPONENTS: Record<string, () => React.ReactElement> = {
  "how-vclaunchkit-works": HowItWorks,
  "why-vibecoders-need-gtm": WhyVibecodersNeedGTM,
  "competitor-analysis-solo-dev": CompetitorAnalysis,
};

/* ── Main page ───────────────────────────────────────────── */

export default function BlogPage() {
  const { user } = useAuth();
  const slug = window.location.pathname.split("/blog/")[1];
  const activePost = slug ? POSTS.find((p) => p.slug === slug) : null;
  const PostContent = activePost ? POST_COMPONENTS[activePost.slug] : null;

  return (
    <div className="min-h-screen bg-bg">
      <SEO
        title={activePost ? activePost.title : "Blog — GTM Strategy for Builders"}
        description={
          activePost
            ? activePost.excerpt
            : "GTM strategy insights, product launch guides, and competitor analysis tips for solo developers and small teams."
        }
        path={activePost ? `/blog/${activePost.slug}` : "/blog"}
      />

      <PublicNav />

      <div className="max-w-3xl mx-auto px-5 py-12">
        {activePost && PostContent ? (
          /* ── Single post view ── */
          <article>
            <Link to="/blog" className="text-sm text-text2 hover:text-accent2 transition-colors">
              &larr; All posts
            </Link>
            <h1 className="text-3xl font-bold mt-4 mb-3 leading-tight">{activePost.title}</h1>
            <div className="flex items-center gap-4 text-sm text-text2 mb-8">
              <span>{activePost.date}</span>
              <span>{activePost.readTime}</span>
              <div className="flex gap-2">
                {activePost.tags.map((t) => (
                  <span key={t} className="text-[10px] px-2 py-0.5 bg-surface2 border border-border rounded-full">
                    {t}
                  </span>
                ))}
              </div>
            </div>

            <PostContent />

            {/* CTA */}
            <div className="mt-12 p-6 bg-surface border border-border rounded-xl text-center">
              <h3 className="font-semibold mb-2">Ready to get your own GTM playbook?</h3>
              <p className="text-sm text-text2 mb-4">Your first analysis is free. Results in under 10 minutes.</p>
              <Link
                to={user ? "/new" : "/login"}
                className="px-6 py-2.5 bg-accent hover:bg-accent2 text-white font-semibold rounded-lg transition-colors inline-block text-sm"
              >
                Get Your Free Playbook
              </Link>
            </div>
          </article>
        ) : (
          /* ── Blog index ── */
          <>
            <div className="text-center mb-10">
              <p className="text-accent2 text-sm font-medium uppercase tracking-wide mb-2">Blog</p>
              <h1 className="text-3xl font-bold mb-3">GTM strategy for builders</h1>
              <p className="text-text2 max-w-xl mx-auto">
                Practical go-to-market insights for solo developers and small teams who ship products.
              </p>
            </div>

            <div className="space-y-4">
              {POSTS.map((post) => (
                <Link
                  key={post.slug}
                  to={`/blog/${post.slug}`}
                  className="block bg-surface border border-border/50 rounded-xl p-6 hover:border-accent/30 transition-colors group"
                >
                  <div className="flex gap-2 mb-2">
                    {post.tags.map((t) => (
                      <span key={t} className="text-[10px] px-2 py-0.5 bg-surface2 border border-border rounded-full text-text2">
                        {t}
                      </span>
                    ))}
                  </div>
                  <h2 className="text-lg font-semibold mb-2 group-hover:text-accent2 transition-colors">
                    {post.title}
                  </h2>
                  <p className="text-sm text-text2 leading-relaxed mb-3">{post.excerpt}</p>
                  <div className="flex items-center justify-between text-xs text-text2/50">
                    <span>{post.date} &middot; {post.readTime}</span>
                    <span className="text-accent2 group-hover:underline">Read &rarr;</span>
                  </div>
                </Link>
              ))}
            </div>

            {/* Blog CTA */}
            <div className="mt-8 p-6 bg-surface border border-accent/20 rounded-xl text-center">
              <h3 className="font-semibold mb-2">Get a GTM playbook for your product</h3>
              <p className="text-sm text-text2 mb-4">
                Paste your URL. In 10 minutes, get page-by-page fixes, competitor intel, copy you can ship today, and a 30/60/90 day plan.
              </p>
              <Link
                to={user ? "/new" : "/login"}
                className="px-6 py-2.5 bg-accent hover:bg-accent2 text-white font-semibold rounded-lg transition-colors inline-block text-sm"
              >
                {user ? "Run Your Analysis" : "Get Your Free Playbook"}
              </Link>
              <p className="text-xs text-text2/40 mt-2">Free. No credit card required.</p>
            </div>
          </>
        )}

        <div className="text-center mt-8">
          <Link to="/" className="text-sm text-text2 hover:text-accent2 transition-colors">
            &larr; Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}
