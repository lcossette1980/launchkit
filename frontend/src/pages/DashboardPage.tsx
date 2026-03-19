import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { listAnalyses, rerunAnalysis } from "../api/analyses";
import { getBillingStatus, syncBilling } from "../api/billing";
import type { JobListItem, BillingStatus } from "../types/api";

const STATUS_COLORS: Record<string, string> = {
  completed: "bg-success/15 text-success",
  running: "bg-accent/15 text-accent2",
  pending: "bg-warning/15 text-warning",
  failed: "bg-danger/15 text-danger",
};

const PLAN_LIMITS: Record<string, number> = { free: 1, pro: 5, agency: 25 };

function timeAgo(iso: string | null): string {
  if (!iso) return "";
  const s = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (s < 60) return "just now";
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  if (s < 86400) return `${Math.floor(s / 3600)}h ago`;
  return new Date(iso).toLocaleDateString();
}

export default function DashboardPage() {
  const { user, refetch } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [analyses, setAnalyses] = useState<JobListItem[]>([]);
  const [billing, setBilling] = useState<BillingStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncMsg, setSyncMsg] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      // If returning from Stripe checkout, sync subscription first
      if (searchParams.get("checkout") === "success") {
        setSyncMsg("Syncing your subscription...");
        // Stripe may take a moment to finalize — retry up to 3 times
        let synced = false;
        for (let attempt = 0; attempt < 3 && !synced; attempt++) {
          if (attempt > 0) await new Promise((r) => setTimeout(r, 2000));
          try {
            const syncResult = await syncBilling();
            if (syncResult.synced && syncResult.plan !== "free") {
              await refetch();
              setSyncMsg(`Plan updated to ${syncResult.plan}!`);
              setTimeout(() => setSyncMsg(null), 4000);
              synced = true;
            }
          } catch { /* retry */ }
        }
        if (!synced) {
          setSyncMsg("Subscription is activating — refresh in a moment.");
          setTimeout(() => setSyncMsg(null), 5000);
        }
        setSearchParams({}, { replace: true });
      }

      const [a, b] = await Promise.all([
        listAnalyses().catch(() => [] as JobListItem[]),
        getBillingStatus().catch(() => null),
      ]);
      setAnalyses(a);
      setBilling(b);
      setLoading(false);
    };
    load();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleRerun = async (id: string) => {
    try {
      const res = await rerunAnalysis(id);
      navigate(`/analysis/${res.job_id}/progress`);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Rerun failed");
    }
  };

  const plan = user?.plan ?? "free";
  const limit = PLAN_LIMITS[plan] ?? 1;
  const used = analyses.filter(
    (a) => a.status !== "failed" && a.created_at && new Date(a.created_at).getMonth() === new Date().getMonth()
  ).length;
  const pct = Math.min((used / limit) * 100, 100);

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-5 py-12">
        <div className="animate-pulse text-text2">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-5 py-8">
      {/* Sync banner */}
      {syncMsg && (
        <div className="mb-4 px-4 py-3 bg-accent/10 border border-accent/30 text-accent2 rounded-lg text-sm font-medium">
          {syncMsg}
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-text2 text-sm mt-1">Your GTM analysis history and usage</p>
        </div>
        <Link
          to="/new"
          className="px-5 py-2.5 bg-accent hover:bg-accent2 text-white font-semibold rounded-lg transition-colors text-sm"
        >
          + New Analysis
        </Link>
      </div>

      {/* Usage + Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {/* Usage meter */}
        <div className="bg-surface border border-border rounded-xl p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-text2 uppercase tracking-wider">Usage this month</span>
            <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${plan === "agency" ? "bg-success/15 text-success" : plan === "pro" ? "bg-accent/15 text-accent2" : "bg-border text-text2"}`}>
              {plan}
            </span>
          </div>
          <div className="bg-surface2 rounded-full h-2 overflow-hidden mb-2">
            <div
              className={`h-full rounded-full transition-all ${pct >= 100 ? "bg-danger" : "bg-accent"}`}
              style={{ width: `${pct}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-text2">
            <span>{used} / {limit} analyses</span>
            {plan === "free" && (
              <Link to="/pricing" className="text-accent2 hover:underline">Upgrade</Link>
            )}
          </div>
        </div>

        {/* Total analyses */}
        <div className="bg-surface border border-border rounded-xl p-5">
          <span className="text-xs font-semibold text-text2 uppercase tracking-wider">Total Analyses</span>
          <p className="text-3xl font-bold text-accent2 mt-2">{analyses.length}</p>
        </div>

        {/* Billing */}
        <div className="bg-surface border border-border rounded-xl p-5">
          <span className="text-xs font-semibold text-text2 uppercase tracking-wider">Subscription</span>
          <p className="text-sm mt-2 text-text">
            {billing?.has_subscription
              ? `${billing.subscription_status} — renews ${billing.current_period_end ? new Date(billing.current_period_end).toLocaleDateString() : "—"}`
              : "No active subscription"
            }
          </p>
          {billing?.has_subscription && (
            <Link to="/settings" className="text-xs text-accent2 hover:underline mt-1 inline-block">Manage</Link>
          )}
        </div>
      </div>

      {/* Analysis history */}
      <div className="bg-surface border border-border rounded-xl">
        <div className="px-5 py-4 border-b border-border">
          <h2 className="text-sm font-semibold text-text2 uppercase tracking-wider">Analysis History</h2>
        </div>
        {analyses.length === 0 ? (
          <div className="text-center py-16 text-text2">
            <p className="text-lg mb-2">No analyses yet</p>
            <p className="text-sm mb-6">Run your first GTM analysis to get started.</p>
            <Link to="/new" className="px-5 py-2.5 bg-accent text-white font-semibold rounded-lg text-sm">
              Run Analysis
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-border">
            {analyses.map((a) => (
              <div
                key={a.job_id}
                className="flex items-center justify-between px-5 py-4 hover:bg-surface2/50 transition-colors cursor-pointer"
                onClick={() => {
                  if (a.status === "completed") navigate(`/analysis/${a.job_id}`);
                  else if (a.status === "running" || a.status === "pending") navigate(`/analysis/${a.job_id}/progress`);
                }}
              >
                <div className="min-w-0 flex-1">
                  <p className="font-semibold text-sm truncate">{a.brand}</p>
                  <p className="text-xs text-text2 truncate">{a.site_url}</p>
                </div>
                <div className="flex items-center gap-3 ml-4 flex-shrink-0">
                  <span className="text-xs text-text2">{timeAgo(a.created_at)}</span>
                  <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${STATUS_COLORS[a.status] ?? STATUS_COLORS.pending}`}>
                    {a.status}
                  </span>
                  {a.status === "completed" && (
                    <button
                      onClick={(e) => { e.stopPropagation(); handleRerun(a.job_id); }}
                      className="text-xs text-text2 border border-border rounded px-2 py-1 hover:border-accent hover:text-accent2 transition-colors"
                    >
                      Re-run
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
