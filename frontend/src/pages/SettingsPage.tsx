import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { getBillingStatus, getPortalUrl } from "../api/billing";
import type { BillingStatus } from "../types/api";
import SEO from "../components/SEO";

export default function SettingsPage() {
  const { user } = useAuth();
  const [billing, setBilling] = useState<BillingStatus | null>(null);

  useEffect(() => {
    getBillingStatus().then(setBilling).catch(() => {});
  }, []);

  const handlePortal = async () => {
    try {
      const res = await getPortalUrl();
      window.location.href = res.portal_url;
    } catch (err) {
      alert(err instanceof Error ? err.message : "No billing account found");
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-5 py-8">
      <SEO title="Settings" description="Manage your VCLaunchKit account, billing, and API keys." path="/settings" />
      <h1 className="text-2xl font-bold mb-8">Settings</h1>

      {/* Profile */}
      <div className="bg-surface border border-border rounded-xl p-6 mb-4">
        <h2 className="text-xs font-semibold text-text2 uppercase tracking-wider mb-4">Profile</h2>
        <div className="space-y-3">
          <div>
            <label className="text-xs text-text2">Email</label>
            <p className="text-sm font-medium">{user?.email}</p>
          </div>
          <div>
            <label className="text-xs text-text2">Name</label>
            <p className="text-sm font-medium">{user?.name}</p>
          </div>
        </div>
      </div>

      {/* Billing */}
      <div className="bg-surface border border-border rounded-xl p-6 mb-4">
        <h2 className="text-xs font-semibold text-text2 uppercase tracking-wider mb-4">Billing & Subscription</h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Current Plan: <span className="text-accent2 capitalize">{user?.plan}</span></p>
              {billing?.current_period_end && (
                <p className="text-xs text-text2 mt-1">
                  {billing.cancel_at_period_end ? "Cancels" : "Renews"} on {new Date(billing.current_period_end).toLocaleDateString()}
                </p>
              )}
            </div>
            {billing?.has_subscription && (
              <button
                onClick={handlePortal}
                className="text-xs border border-border rounded-lg px-3 py-1.5 text-text2 hover:border-accent hover:text-accent2 transition-colors"
              >
                Manage Subscription
              </button>
            )}
          </div>
        </div>
      </div>

      {/* API Keys (placeholder) */}
      <div className="bg-surface border border-border rounded-xl p-6">
        <h2 className="text-xs font-semibold text-text2 uppercase tracking-wider mb-4">API Keys</h2>
        <p className="text-sm text-text2">API key management coming soon for Agency plan users.</p>
      </div>
    </div>
  );
}
