import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import SEO from "../components/SEO";

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

function PostContent({ slug }: { slug: string }) {
  if (slug === "how-vclaunchkit-works") {
    return (
      <div className="prose-sm">
        <p>
          Most solo developers and small teams build incredible products — but when it comes to
          go-to-market strategy, they're stuck Googling "how to launch a SaaS" and piecing
          together generic advice from blog posts written for Series B companies with 50-person
          marketing teams.
        </p>
        <p className="mt-4">
          We built VCLaunchKit to solve this. Here's exactly what happens when you paste your URL:
        </p>

        <h3 className="text-lg font-semibold mt-8 mb-3">Step 1: 9 AI agents analyze your site</h3>
        <p>
          When you submit a URL, our pipeline kicks off 9 specialized AI agents. The first three
          run a "quick scan" — planning what to analyze, crawling your entire site (following
          sitemaps and internal links), and scoring every page on clarity, audience fit, conversion
          potential, SEO, and UX. You see initial scores within 3 minutes while the deep analysis
          continues.
        </p>

        <h3 className="text-lg font-semibold mt-8 mb-3">Step 2: Market research and competitor analysis</h3>
        <p>
          The next agents research your market — trends, target audience definition, keyword
          opportunities, and content topics. Then they find and deep-dive 5+ competitors: their
          value proposition, pricing model, strengths, weaknesses, and content strategy. This isn't
          surface-level — it's the kind of analysis a marketing consultant charges $5K+ for.
        </p>

        <h3 className="text-lg font-semibold mt-8 mb-3">Step 3: Strategy, experiments, and copy</h3>
        <p>
          The final agents generate your GTM strategy (positioning, channels, partnerships,
          pricing recommendations), a backlog of 15+ growth experiments ranked by ICE score,
          and a complete copy kit — headlines, email templates, LinkedIn messages, ad copy for
          3 platforms, and a full landing page blueprint with problem/solution/benefits/FAQ sections.
        </p>

        <h3 className="text-lg font-semibold mt-8 mb-3">What you get</h3>
        <p>
          The final output is a 10-section GTM playbook with a 30/60/90 day roadmap telling you
          exactly what to do this week, this month, and next quarter. Everything is specific to
          your product and audience — not generic advice.
        </p>
        <p className="mt-4">
          You can export it as HTML, PDF, or JSON. Share it with a public link. Re-run it monthly
          to track improvements. And your first analysis is free.
        </p>
      </div>
    );
  }
  return null;
}

export default function BlogPage() {
  const { user } = useAuth();
  const slug = window.location.pathname.split("/blog/")[1];
  const activePost = slug ? POSTS.find((p) => p.slug === slug) : null;

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

      {/* Nav */}
      <nav className="border-b border-border/50 bg-bg/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-5 flex items-center justify-between h-14">
          <Link to="/" className="text-lg font-bold tracking-tight">
            <span className="text-accent2">VC</span>LaunchKit
          </Link>
          <div className="flex items-center gap-4">
            <Link to="/examples" className="text-sm text-text2 hover:text-text transition-colors">Examples</Link>
            <Link to="/pricing" className="text-sm text-text2 hover:text-text transition-colors">Pricing</Link>
            {user ? (
              <Link to="/dashboard" className="px-4 py-1.5 bg-accent hover:bg-accent2 text-white text-sm font-semibold rounded-lg transition-colors">
                Dashboard
              </Link>
            ) : (
              <Link to="/login" className="px-4 py-1.5 bg-accent hover:bg-accent2 text-white text-sm font-semibold rounded-lg transition-colors">
                Sign In
              </Link>
            )}
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-5 py-12">
        {activePost ? (
          /* ── Single post view ── */
          <article>
            <Link to="/blog" className="text-sm text-text2 hover:text-accent2 transition-colors">
              &larr; All posts
            </Link>
            <h1 className="text-3xl font-bold mt-4 mb-3">{activePost.title}</h1>
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
            <div className="text-text2 leading-relaxed">
              <PostContent slug={activePost.slug} />
            </div>

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
