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
  featured?: boolean;
}

const POSTS: BlogPost[] = [
  {
    slug: "how-we-score-websites",
    title: "How we score websites: the methodology behind VCLaunchKit's 5 metrics",
    excerpt:
      "Every VCLaunchKit report scores your site on clarity, audience fit, conversion, SEO, and UX. Here's exactly what each score measures, how the rubric works, and what the numbers actually mean for your business.",
    date: "March 21, 2026",
    readTime: "7 min read",
    tags: ["Methodology", "Deep Dive"],
    featured: true,
  },
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

function HowWeScoreWebsites() {
  return (
    <div className="space-y-6 text-[15px] leading-relaxed text-text2">
      <p>
        Every VCLaunchKit report gives your site a score from 0-100 on five dimensions: <strong className="text-text">Clarity</strong>, <strong className="text-text">Audience Fit</strong>, <strong className="text-text">Conversion</strong>, <strong className="text-text">SEO</strong>, and <strong className="text-text">UX</strong>.
        These aren't arbitrary numbers. Each score follows a specific rubric, grounded in evidence from your actual pages. Here's exactly how each one works and what it means for your business.
      </p>

      <h3 className="text-xl font-semibold text-text mt-10 mb-3">Why five metrics (and why these five)</h3>
      <p>
        We chose these five because they cover the complete visitor journey. A visitor lands on your site (UX), tries to understand what you offer (Clarity), decides if it's for them (Audience Fit), looks for a way to take action (Conversion), and ideally found you through search in the first place (SEO). If any one of these breaks down, you lose that visitor.
      </p>
      <p>
        Most website audit tools focus on technical SEO or page speed. Those matter, but they miss the human side — is your message clear? Does your CTA actually stand out? Does your copy speak to your target customer? Our scoring system covers both the technical and the human.
      </p>

      <h3 className="text-xl font-semibold text-text mt-10 mb-3">1. Clarity (0-100)</h3>
      <p className="italic text-text/80 mb-3">Can a visitor understand what you do within 5 seconds?</p>
      <p>Clarity measures how well your page communicates its purpose. We look at:</p>
      <ul className="list-disc pl-6 space-y-2 mt-3">
        <li><strong className="text-text">Headline specificity:</strong> Does the H1 state a concrete outcome, or is it vague? "Stop guessing your GTM" is specific. "Welcome to our platform" is not.</li>
        <li><strong className="text-text">Value proposition visibility:</strong> Can the visitor see what they'll get without scrolling? Is there a clear subheadline that elaborates?</li>
        <li><strong className="text-text">Message consistency:</strong> Do the headline, subheadline, and CTA all point in the same direction, or do they contradict each other?</li>
        <li><strong className="text-text">Jargon level:</strong> Are you using industry terms your audience understands, or internal language they wouldn't?</li>
      </ul>
      <div className="bg-surface border border-border/50 rounded-lg p-4 mt-4">
        <p className="text-xs text-accent2 font-semibold uppercase tracking-wider mb-2">Scoring rubric</p>
        <div className="space-y-1 text-sm">
          <p><strong className="text-text">90-100:</strong> Instantly clear value prop. No confusion about what this product does.</p>
          <p><strong className="text-text">70-89:</strong> Purpose is clear, but messaging could be sharper or more specific.</p>
          <p><strong className="text-text">50-69:</strong> Takes effort to understand. Mixed messages or vague copy.</p>
          <p><strong className="text-text">30-49:</strong> Confusing. Unclear what the product or service actually is.</p>
          <p><strong className="text-text">0-29:</strong> No discernible message or purpose.</p>
        </div>
      </div>
      <p className="mt-4">
        <strong className="text-text">What a low clarity score means for your business:</strong> Visitors bounce before they understand your product. You're paying for traffic (or working for organic traffic) and losing people in the first 5 seconds. This is typically the cheapest problem to fix — it's a copywriting issue, not a technical one.
      </p>

      <h3 className="text-xl font-semibold text-text mt-10 mb-3">2. Audience Fit (0-100)</h3>
      <p className="italic text-text/80 mb-3">Does your content speak directly to your target customer?</p>
      <p>Audience fit measures alignment between your content and the people you're trying to reach. We evaluate:</p>
      <ul className="list-disc pl-6 space-y-2 mt-3">
        <li><strong className="text-text">Language match:</strong> Are you using the words your audience uses to describe their problems? A developer audience expects different language than a marketing team.</li>
        <li><strong className="text-text">Pain point relevance:</strong> Do you address the specific frustrations and goals of your target audience, or are you speaking in generalities?</li>
        <li><strong className="text-text">Social proof alignment:</strong> Do your testimonials feature people who look like your target customer? A quote from a "Fortune 500 VP" won't resonate with solo developers.</li>
        <li><strong className="text-text">Feature framing:</strong> Are features described in terms your audience cares about? "Enterprise-grade security" means nothing to an indie hacker. "Your data stays private" does.</li>
      </ul>
      <div className="bg-surface border border-border/50 rounded-lg p-4 mt-4">
        <p className="text-xs text-accent2 font-semibold uppercase tracking-wider mb-2">Scoring rubric</p>
        <div className="space-y-1 text-sm">
          <p><strong className="text-text">90-100:</strong> Every element speaks directly to the target audience's language and needs.</p>
          <p><strong className="text-text">70-89:</strong> Good fit, but some elements feel generic or off-target.</p>
          <p><strong className="text-text">50-69:</strong> Partially aligned. Some content targets different personas.</p>
          <p><strong className="text-text">30-49:</strong> Weak alignment. Mostly generic content.</p>
          <p><strong className="text-text">0-29:</strong> Content clearly targets a different audience.</p>
        </div>
      </div>
      <p className="mt-4">
        <strong className="text-text">What a low audience fit score means:</strong> You're attracting the wrong visitors, or the right visitors don't recognize themselves in your messaging. This leads to high bounce rates from qualified traffic — the most expensive kind of waste.
      </p>

      <h3 className="text-xl font-semibold text-text mt-10 mb-3">3. Conversion (0-100)</h3>
      <p className="italic text-text/80 mb-3">How effectively does the page drive visitors to take action?</p>
      <p>Conversion measures the strength of your calls-to-action and the friction in your signup/purchase flow:</p>
      <ul className="list-disc pl-6 space-y-2 mt-3">
        <li><strong className="text-text">CTA visibility:</strong> Can visitors see the primary action without scrolling? Is it visually distinct from the rest of the page?</li>
        <li><strong className="text-text">CTA clarity:</strong> Does the button text tell people exactly what happens next? "Get Your Free Playbook" beats "Submit" or "Learn More."</li>
        <li><strong className="text-text">CTA repetition:</strong> Is there a CTA at multiple scroll points, or just one at the top that visitors scroll past?</li>
        <li><strong className="text-text">Trust signals:</strong> Are there elements that reduce anxiety? "No credit card required," testimonials near the CTA, security badges, money-back guarantees.</li>
        <li><strong className="text-text">Friction level:</strong> How many steps/fields between "I'm interested" and "I'm using it"? Every extra field costs conversions.</li>
      </ul>
      <div className="bg-surface border border-border/50 rounded-lg p-4 mt-4">
        <p className="text-xs text-accent2 font-semibold uppercase tracking-wider mb-2">Scoring rubric</p>
        <div className="space-y-1 text-sm">
          <p><strong className="text-text">90-100:</strong> Multiple clear CTAs, low friction, strong urgency and trust signals.</p>
          <p><strong className="text-text">70-89:</strong> CTAs present and visible, but could be stronger or repeated more.</p>
          <p><strong className="text-text">50-69:</strong> CTAs exist but weak visibility, missing trust signals, or high friction.</p>
          <p><strong className="text-text">30-49:</strong> Hard to find CTAs. Significant conversion barriers.</p>
          <p><strong className="text-text">0-29:</strong> No clear conversion path at all.</p>
        </div>
      </div>
      <p className="mt-4">
        <strong className="text-text">What a low conversion score means:</strong> People understand your product and think it's relevant — but they're not taking action. This is the highest-leverage score to improve because small changes (button color, copy, placement) can produce measurable results within days.
      </p>

      <h3 className="text-xl font-semibold text-text mt-10 mb-3">4. SEO (0-100)</h3>
      <p className="italic text-text/80 mb-3">How well is this page optimized for search engines?</p>
      <p>SEO measures the technical and content foundations that determine whether search engines can find, understand, and rank your page:</p>
      <ul className="list-disc pl-6 space-y-2 mt-3">
        <li><strong className="text-text">Heading hierarchy:</strong> Is there one H1, followed by logical H2s and H3s? Do headings contain relevant keywords?</li>
        <li><strong className="text-text">Meta tags:</strong> Does the page have a descriptive title tag and meta description? Are they the right length and keyword-optimized?</li>
        <li><strong className="text-text">Content depth:</strong> Is there enough substantive content for search engines to understand the page's topic?</li>
        <li><strong className="text-text">Image optimization:</strong> Do images have alt text? Are they appropriately sized?</li>
        <li><strong className="text-text">Internal linking:</strong> Does the page link to other relevant pages on the site?</li>
      </ul>
      <div className="bg-surface border border-border/50 rounded-lg p-4 mt-4">
        <p className="text-xs text-accent2 font-semibold uppercase tracking-wider mb-2">Scoring rubric</p>
        <div className="space-y-1 text-sm">
          <p><strong className="text-text">90-100:</strong> Excellent heading hierarchy, meta tags, keywords, and structured data.</p>
          <p><strong className="text-text">70-89:</strong> Good basics, but missing some optimization opportunities.</p>
          <p><strong className="text-text">50-69:</strong> Some SEO elements present but inconsistent or incomplete.</p>
          <p><strong className="text-text">30-49:</strong> Minimal SEO effort. Missing critical elements.</p>
          <p><strong className="text-text">0-29:</strong> No SEO optimization visible.</p>
        </div>
      </div>
      <p className="mt-4">
        <strong className="text-text">What a low SEO score means:</strong> You're invisible to people actively searching for what you offer. Unlike paid ads, SEO compounds over time — fixing these issues now means more free, qualified traffic every month going forward.
      </p>

      <h3 className="text-xl font-semibold text-text mt-10 mb-3">5. UX (0-100)</h3>
      <p className="italic text-text/80 mb-3">Does the page feel professional, fast, and easy to use?</p>
      <p>UX measures the overall user experience — the impression your site makes beyond the words on the page:</p>
      <ul className="list-disc pl-6 space-y-2 mt-3">
        <li><strong className="text-text">Load performance:</strong> How fast does the page load? We measure actual load time, DOM ready, and first paint metrics.</li>
        <li><strong className="text-text">Navigation clarity:</strong> Can visitors find what they're looking for? Is the menu structure intuitive?</li>
        <li><strong className="text-text">Visual hierarchy:</strong> Does the page guide the eye naturally, or is it a wall of text with no structure?</li>
        <li><strong className="text-text">Mobile responsiveness:</strong> Does the page work on phones? Are tap targets large enough? Is text readable without zooming?</li>
        <li><strong className="text-text">Content completeness:</strong> Is any text truncated? Are there broken images or dead links? Does everything look polished?</li>
      </ul>
      <div className="bg-surface border border-border/50 rounded-lg p-4 mt-4">
        <p className="text-xs text-accent2 font-semibold uppercase tracking-wider mb-2">Scoring rubric</p>
        <div className="space-y-1 text-sm">
          <p><strong className="text-text">90-100:</strong> Smooth navigation, fast loading, accessible, polished design.</p>
          <p><strong className="text-text">70-89:</strong> Good UX with minor issues (layout, responsiveness, etc.).</p>
          <p><strong className="text-text">50-69:</strong> Functional but noticeable UX problems (truncated text, poor nav).</p>
          <p><strong className="text-text">30-49:</strong> Significant UX barriers that hurt engagement.</p>
          <p><strong className="text-text">0-29:</strong> Broken or unusable experience.</p>
        </div>
      </div>
      <p className="mt-4">
        <strong className="text-text">What a low UX score means:</strong> Even if your product is great, a poor user experience erodes trust. Visitors unconsciously judge your product's quality by the quality of your website. Broken layouts, slow loading, or clunky navigation signal "this team doesn't pay attention to details."
      </p>

      <h3 className="text-xl font-semibold text-text mt-10 mb-3">How the analysis actually works</h3>
      <p>
        Each page on your site goes through a three-layer analysis:
      </p>
      <ul className="list-disc pl-6 space-y-2 mt-3">
        <li><strong className="text-text">Structural analysis:</strong> Our crawler extracts headings, CTAs, forms, meta tags, images, and links — the skeleton of your page.</li>
        <li><strong className="text-text">Content analysis:</strong> The visible text is extracted and evaluated for messaging quality, audience alignment, and keyword usage.</li>
        <li><strong className="text-text">Visual analysis:</strong> We capture a screenshot of what visitors actually see and evaluate design quality, CTA prominence, visual hierarchy, and mobile responsiveness.</li>
      </ul>
      <p className="mt-4">
        All three layers feed into the scoring. This means a page with perfect SEO meta tags but a confusing headline will still get dinged on Clarity. A page with a beautiful design but no CTA will still get a low Conversion score. The scores reflect the complete picture.
      </p>

      <h3 className="text-xl font-semibold text-text mt-10 mb-3">What to do with your scores</h3>
      <p>
        The scores tell you <em>where</em> to focus. The recommendations tell you <em>what</em> to do. Here's a simple priority framework:
      </p>
      <ul className="list-disc pl-6 space-y-2 mt-3">
        <li><strong className="text-text">Fix Conversion first</strong> — if people arrive but don't act, you're wasting every other investment. CTA improvements are typically the fastest, cheapest fix.</li>
        <li><strong className="text-text">Fix Clarity second</strong> — if people can't understand your product, nothing else matters. This is usually a copywriting exercise.</li>
        <li><strong className="text-text">Fix Audience Fit third</strong> — make sure you're speaking your customer's language, not yours.</li>
        <li><strong className="text-text">Fix SEO for compounding growth</strong> — SEO takes time to show results, but the payoff is free traffic that grows over months.</li>
        <li><strong className="text-text">Fix UX for polish</strong> — UX improvements build trust and reduce friction, but they're most impactful after the fundamentals above are solid.</li>
      </ul>
      <p className="mt-4">
        Every VCLaunchKit report includes specific, page-level recommendations for each metric — not generic advice, but actions grounded in what we found on your actual pages. The top 3 priorities and quick wins sections distill everything into what you should do this week.
      </p>
    </div>
  );
}

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
  "how-we-score-websites": HowWeScoreWebsites,
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

            {/* Featured post */}
            {POSTS.filter((p) => p.featured).map((post) => (
              <Link
                key={post.slug}
                to={`/blog/${post.slug}`}
                className="block bg-surface border border-accent/30 rounded-xl p-8 hover:border-accent/50 transition-colors group mb-6 ring-1 ring-accent/10"
              >
                <div className="flex gap-2 mb-3">
                  <span className="text-[10px] px-2 py-0.5 bg-accent/10 border border-accent/30 rounded-full text-accent2 font-semibold">
                    Featured
                  </span>
                  {post.tags.map((t) => (
                    <span key={t} className="text-[10px] px-2 py-0.5 bg-surface2 border border-border rounded-full text-text2">
                      {t}
                    </span>
                  ))}
                </div>
                <h2 className="text-xl font-bold mb-3 group-hover:text-accent2 transition-colors leading-tight">
                  {post.title}
                </h2>
                <p className="text-sm text-text2 leading-relaxed mb-4">{post.excerpt}</p>
                <div className="flex items-center justify-between text-xs text-text2/50">
                  <span>{post.date} &middot; {post.readTime}</span>
                  <span className="text-accent2 font-medium group-hover:underline">Read the deep dive &rarr;</span>
                </div>
              </Link>
            ))}

            {/* Other posts */}
            <div className="space-y-4">
              {POSTS.filter((p) => !p.featured).map((post) => (
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
