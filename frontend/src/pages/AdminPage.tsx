import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import SEO from "../components/SEO";
import {
  getAdminStats,
  getAdminUsers,
  getAdminReports,
  toggleAdmin,
  setUserPlan,
  toggleReportPublic,
  adminRerun,
  type AdminStats,
  type AdminUser,
  type AdminReport,
} from "../api/admin";

function StatCard({ label, value, sub }: { label: string; value: string | number; sub?: string }) {
  return (
    <div className="bg-surface border border-border rounded-lg p-4">
      <p className="text-xs text-text2 uppercase tracking-wider">{label}</p>
      <p className="text-2xl font-bold text-accent2 mt-1">{value}</p>
      {sub && <p className="text-xs text-text2 mt-0.5">{sub}</p>}
    </div>
  );
}

function scoreColor(v: number) {
  if (v >= 75) return "text-green-400";
  if (v >= 50) return "text-yellow-400";
  return "text-red-400";
}

export default function AdminPage() {
  const { user } = useAuth();
  const [tab, setTab] = useState<"overview" | "users" | "reports">("overview");
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [reports, setReports] = useState<AdminReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      const [s, u, r] = await Promise.all([
        getAdminStats(),
        getAdminUsers(),
        getAdminReports(100),
      ]);
      setStats(s);
      setUsers(u);
      setReports(r);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load admin data");
    } finally {
      setLoading(false);
    }
  }

  async function handleToggleAdmin(userId: string) {
    await toggleAdmin(userId);
    const u = await getAdminUsers();
    setUsers(u);
  }

  async function handleSetPlan(userId: string, plan: string) {
    await setUserPlan(userId, plan);
    const u = await getAdminUsers();
    setUsers(u);
  }

  async function handleTogglePublic(jobId: string) {
    await toggleReportPublic(jobId);
    const r = await getAdminReports(100);
    setReports(r);
  }

  async function handleRerun(jobId: string) {
    if (!confirm("Re-run this analysis?")) return;
    const result = await adminRerun(jobId);
    alert(`Re-run started: ${result.job_id}`);
    const r = await getAdminReports(100);
    setReports(r);
  }

  if (!user?.is_admin) {
    return (
      <div className="max-w-2xl mx-auto px-5 py-20 text-center">
        <h1 className="text-2xl font-bold mb-4">Access Denied</h1>
        <p className="text-text2">Admin privileges required.</p>
        <Link to="/dashboard" className="text-accent2 text-sm mt-4 inline-block">Back to Dashboard</Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-5 py-8">
      <SEO title="Admin" description="VCLaunchKit admin dashboard" path="/admin" />

      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Admin Dashboard</h1>
        <button onClick={loadData} className="text-xs text-text2 border border-border rounded px-3 py-1.5 hover:border-accent hover:text-accent2 transition-colors">
          Refresh
        </button>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-6 text-sm text-red-400">{error}</div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 mb-6 border-b border-border pb-1">
        {(["overview", "users", "reports"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
              tab === t ? "bg-accent/10 text-accent2 border-b-2 border-accent" : "text-text2 hover:text-text"
            }`}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-center py-20 text-text2 animate-pulse">Loading...</div>
      ) : tab === "overview" && stats ? (
        <div className="space-y-8">
          {/* Key metrics */}
          <div>
            <h2 className="text-sm font-semibold text-text2 uppercase tracking-wider mb-3">Platform Overview</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <StatCard label="Total Users" value={stats.users.total} sub={`${stats.users.active} active`} />
              <StatCard label="Total Analyses" value={stats.analyses.total} sub={`${stats.analyses.completed} completed`} />
              <StatCard label="Active Subs" value={stats.billing.active_subscriptions} sub={`${stats.billing.pro_subscribers} pro, ${stats.billing.agency_subscribers} agency`} />
              <StatCard label="Est. MRR" value={`$${stats.billing.estimated_mrr}`} />
            </div>
          </div>

          {/* Usage & costs */}
          <div>
            <h2 className="text-sm font-semibold text-text2 uppercase tracking-wider mb-3">This Month</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <StatCard label="Analyses Run" value={stats.costs.analyses_this_month} />
              <StatCard label="Est. API Cost" value={`$${stats.costs.estimated_cost}`} sub={`$${stats.costs.cost_per_analysis}/analysis`} />
              <StatCard label="Running Now" value={stats.analyses.running} />
              <StatCard label="Failed" value={stats.analyses.failed} />
            </div>
          </div>

          {/* Plan breakdown */}
          <div>
            <h2 className="text-sm font-semibold text-text2 uppercase tracking-wider mb-3">Users by Plan</h2>
            <div className="grid grid-cols-3 gap-3">
              {Object.entries(stats.users.by_plan).map(([plan, count]) => (
                <StatCard key={plan} label={plan} value={count} />
              ))}
            </div>
          </div>
        </div>
      ) : tab === "users" ? (
        <div>
          <p className="text-xs text-text2 mb-4">{users.length} users</p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-text2 text-xs uppercase tracking-wider">
                  <th className="pb-2 pr-4">Email</th>
                  <th className="pb-2 pr-4">Plan</th>
                  <th className="pb-2 pr-4">Analyses</th>
                  <th className="pb-2 pr-4">Admin</th>
                  <th className="pb-2 pr-4">Joined</th>
                  <th className="pb-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} className="border-b border-border/50 hover:bg-surface2/50">
                    <td className="py-3 pr-4">
                      <div className="font-medium">{u.email}</div>
                      <div className="text-xs text-text2">{u.name}</div>
                    </td>
                    <td className="py-3 pr-4">
                      <select
                        value={u.plan}
                        onChange={(e) => handleSetPlan(u.id, e.target.value)}
                        className="bg-surface2 border border-border rounded px-2 py-1 text-xs"
                      >
                        <option value="free">Free</option>
                        <option value="pro">Pro</option>
                        <option value="agency">Agency</option>
                      </select>
                    </td>
                    <td className="py-3 pr-4 text-text2">
                      {u.analyses_this_month} / {u.analyses_total} total
                    </td>
                    <td className="py-3 pr-4">
                      <button
                        onClick={() => handleToggleAdmin(u.id)}
                        className={`text-xs px-2 py-0.5 rounded ${u.is_admin ? "bg-accent/15 text-accent2" : "bg-surface2 text-text2"}`}
                      >
                        {u.is_admin ? "Admin" : "User"}
                      </button>
                    </td>
                    <td className="py-3 pr-4 text-xs text-text2">
                      {u.created_at ? new Date(u.created_at).toLocaleDateString() : "—"}
                    </td>
                    <td className="py-3">
                      {u.subscription_status && (
                        <span className="text-xs text-green-400">{u.subscription_status}</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : tab === "reports" ? (
        <div>
          <p className="text-xs text-text2 mb-4">{reports.length} reports</p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-text2 text-xs uppercase tracking-wider">
                  <th className="pb-2 pr-4">Brand</th>
                  <th className="pb-2 pr-4">User</th>
                  <th className="pb-2 pr-4">Status</th>
                  <th className="pb-2 pr-4">Scores</th>
                  <th className="pb-2 pr-4">Public</th>
                  <th className="pb-2 pr-4">Date</th>
                  <th className="pb-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((r) => {
                  const vals = Object.values(r.scores || {}).filter((v): v is number => typeof v === "number");
                  const avg = vals.length ? Math.round(vals.reduce((a, b) => a + b, 0) / vals.length) : 0;
                  return (
                    <tr key={r.id} className="border-b border-border/50 hover:bg-surface2/50">
                      <td className="py-3 pr-4">
                        <div className="font-medium">{r.brand}</div>
                        <div className="text-xs text-text2 truncate max-w-[200px]">{r.site_url}</div>
                      </td>
                      <td className="py-3 pr-4 text-xs text-text2">{r.user_email}</td>
                      <td className="py-3 pr-4">
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          r.status === "completed" ? "bg-green-500/15 text-green-400" :
                          r.status === "running" ? "bg-accent/15 text-accent2" :
                          r.status === "failed" ? "bg-red-500/15 text-red-400" :
                          "bg-yellow-500/15 text-yellow-400"
                        }`}>
                          {r.status}
                        </span>
                      </td>
                      <td className="py-3 pr-4">
                        {avg > 0 ? <span className={`font-bold ${scoreColor(avg)}`}>{avg}</span> : <span className="text-text2">—</span>}
                      </td>
                      <td className="py-3 pr-4">
                        <button
                          onClick={() => handleTogglePublic(r.id)}
                          className={`text-xs px-2 py-0.5 rounded ${r.is_public ? "bg-green-500/15 text-green-400" : "bg-surface2 text-text2"}`}
                        >
                          {r.is_public ? "Public" : "Private"}
                        </button>
                      </td>
                      <td className="py-3 pr-4 text-xs text-text2">
                        {r.created_at ? new Date(r.created_at).toLocaleDateString() : "—"}
                      </td>
                      <td className="py-3">
                        <div className="flex gap-2">
                          {r.has_results && r.share_token && (
                            <Link to={`/share/${r.share_token}`} className="text-xs text-accent2 hover:underline">View</Link>
                          )}
                          <button onClick={() => handleRerun(r.id)} className="text-xs text-text2 hover:text-accent2">Re-run</button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}
    </div>
  );
}
