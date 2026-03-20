import { api } from "./client";

export interface AdminStats {
  users: { total: number; active: number; by_plan: Record<string, number> };
  analyses: { total: number; completed: number; failed: number; running: number; this_month: number };
  billing: { active_subscriptions: number; pro_subscribers: number; agency_subscribers: number; estimated_mrr: number };
  costs: { analyses_this_month: number; estimated_cost: number; cost_per_analysis: number };
}

export interface AdminUser {
  id: string;
  email: string;
  name: string;
  plan: string;
  is_admin: boolean;
  is_active: boolean;
  email_verified: boolean;
  stripe_customer_id: string | null;
  created_at: string | null;
  analyses_total: number;
  analyses_this_month: number;
  subscription_status: string | null;
}

export interface AdminReport {
  id: string;
  brand: string;
  site_url: string;
  status: string;
  progress_pct: number;
  current_step: string;
  user_email: string;
  user_plan: string;
  scores: Record<string, number>;
  has_results: boolean;
  share_token: string | null;
  is_public: boolean;
  error_message: string | null;
  created_at: string | null;
  completed_at: string | null;
}

export async function getAdminStats(): Promise<AdminStats> {
  return api("/admin/stats");
}

export async function getAdminUsers(limit = 50): Promise<AdminUser[]> {
  return api(`/admin/users?limit=${limit}`);
}

export async function getAdminReports(limit = 50, status?: string): Promise<AdminReport[]> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (status) params.set("status", status);
  return api(`/admin/reports?${params}`);
}

export async function toggleAdmin(userId: string): Promise<{ email: string; is_admin: boolean }> {
  return api(`/admin/users/${userId}/toggle-admin`, { method: "POST" });
}

export async function setUserPlan(userId: string, plan: string): Promise<{ email: string; plan: string }> {
  return api(`/admin/users/${userId}/set-plan?plan=${plan}`, { method: "POST" });
}

export async function toggleReportPublic(jobId: string): Promise<{ id: string; is_public: boolean }> {
  return api(`/admin/reports/${jobId}/toggle-public`, { method: "POST" });
}

export async function adminRerun(jobId: string): Promise<{ job_id: string; status: string }> {
  return api(`/admin/reports/${jobId}/rerun`, { method: "POST" });
}
