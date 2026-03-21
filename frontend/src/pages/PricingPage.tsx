import { useAuth } from "../context/AuthContext";
import { createCheckout } from "../api/billing";
import { Link } from "react-router-dom";
import PublicNav from "../components/PublicNav";
import SEO from "../components/SEO";

const PLANS = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    features: ["1 analysis/month", "Executive summary only", "Overall scores", "Top 3 priorities"],
    cta: "Current Plan",
    key: "free" as const,
    featured: false,
  },
  {
    name: "Pro",
    price: "$29",
    period: "/month",
    features: ["5 analyses/month", "Full page-by-page breakdown", "Copy kit + email templates", "30/60/90 roadmap", "Competitor deep-dives", "Re-run & track changes", "HTML/JSON export", "3 brands"],
    cta: "Upgrade to Pro",
    key: "pro" as const,
    featured: true,
  },
  {
    name: "Agency",
    price: "$79",
    period: "/month",
    features: ["25 analyses/month", "Everything in Pro", "Unlimited brands", "API access", "Priority support"],
    cta: "Upgrade to Agency",
    key: "agency" as const,
    featured: false,
  },
];

export default function PricingPage() {
  const { user } = useAuth();

  const handleUpgrade = async (plan: "pro" | "agency") => {
    if (!user) return;
    try {
      const res = await createCheckout(plan);
      window.location.href = res.checkout_url;
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to create checkout");
    }
  };

  return (
    <div className="min-h-screen bg-bg">
      <SEO title="Pricing" description="Simple, transparent pricing for solo developers and small teams. Start free, upgrade to Pro ($29/mo) or Agency ($79/mo) when you need more." path="/pricing" />
      <PublicNav />

      {/* Pricing content */}
      <div className="max-w-4xl mx-auto px-5 py-12">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold mb-2">Simple, transparent pricing</h1>
          <p className="text-text2">AI-powered GTM playbooks for builders who ship.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {PLANS.map((plan) => {
            const isCurrent = user?.plan === plan.key;
            return (
              <div
                key={plan.key}
                className={`bg-surface border rounded-xl p-6 text-center ${plan.featured ? "border-accent ring-1 ring-accent/20" : "border-border"}`}
              >
                <h3 className="text-lg font-bold mb-1">{plan.name}</h3>
                <div className="mb-4">
                  <span className="text-3xl font-bold text-accent2">{plan.price}</span>
                  <span className="text-sm text-text2">{plan.period}</span>
                </div>
                <ul className="text-left text-sm text-text2 space-y-2 mb-6">
                  {plan.features.map((f, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-accent2 font-bold mt-0.5">&#10003;</span>
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>
                {isCurrent ? (
                  <div className="py-2.5 text-sm font-semibold text-text2 border border-border rounded-lg">
                    Current Plan
                  </div>
                ) : plan.key === "free" ? (
                  <div className="py-2.5 text-sm text-text2">Free forever</div>
                ) : user ? (
                  <button
                    onClick={() => handleUpgrade(plan.key)}
                    className={`w-full py-2.5 text-sm font-semibold rounded-lg transition-colors ${
                      plan.featured
                        ? "bg-accent hover:bg-accent2 text-white"
                        : "bg-surface2 border border-border text-text hover:border-accent"
                    }`}
                  >
                    {plan.cta}
                  </button>
                ) : (
                  <Link
                    to="/login"
                    className={`block w-full py-2.5 text-sm font-semibold rounded-lg text-center transition-colors ${
                      plan.featured
                        ? "bg-accent hover:bg-accent2 text-white"
                        : "bg-surface2 border border-border text-text hover:border-accent"
                    }`}
                  >
                    Get Started
                  </Link>
                )}
              </div>
            );
          })}
        </div>

        {/* FAQ */}
        <div className="mt-16 max-w-2xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-8">Frequently asked questions</h2>
          <div className="space-y-4">
            {[
              {
                q: "What do I get with the free plan?",
                a: "One analysis per month with an executive summary, overall website scores, and your top 3 priorities. Enough to see the value before upgrading.",
              },
              {
                q: "What's in a full Pro report?",
                a: "Page-by-page audit with scores, 5+ competitor deep-dives, a copy kit with headlines and email templates, ad copy for 3 platforms, growth experiments ranked by ICE score, market research, and a 30/60/90 day roadmap.",
              },
              {
                q: "How long does an analysis take?",
                a: "About 8-10 minutes. 9 AI agents crawl your site, research your market, analyze competitors, and generate a complete GTM playbook.",
              },
              {
                q: "Can I cancel anytime?",
                a: "Yes. No contracts, no cancellation fees. Your plan stays active until the end of the billing period.",
              },
              {
                q: "What does 'brands' mean in the plan limits?",
                a: "A brand is a distinct website or product you analyze. Free gets 1, Pro gets 3, Agency gets unlimited. Perfect if you manage multiple products or client sites.",
              },
              {
                q: "Do I need marketing experience?",
                a: "No. Reports are written in plain language with specific, actionable steps. Every recommendation tells you what to do, why, and how.",
              },
            ].map((faq, i) => (
              <details key={i} className="group bg-surface border border-border/50 rounded-xl">
                <summary className="flex items-center justify-between p-5 cursor-pointer text-sm font-medium hover:text-accent2 transition-colors">
                  {faq.q}
                  <span className="text-text2 group-open:rotate-45 transition-transform text-lg ml-3">+</span>
                </summary>
                <div className="px-5 pb-5 pt-0 text-sm text-text2 leading-relaxed">
                  {faq.a}
                </div>
              </details>
            ))}
          </div>
        </div>

        {/* Back link */}
        <div className="text-center mt-8">
          <Link
            to={user ? "/dashboard" : "/"}
            className="text-sm text-text2 hover:text-accent2 transition-colors"
          >
            &larr; {user ? "Back to Dashboard" : "Back to Home"}
          </Link>
        </div>
      </div>
    </div>
  );
}
