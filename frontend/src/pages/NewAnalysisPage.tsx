import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { startAnalysis } from "../api/analyses";
import { ApiError } from "../api/client";
import type { AnalysisRequest } from "../types/api";

export default function NewAnalysisPage() {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    const fd = new FormData(e.currentTarget);
    const req: AnalysisRequest = {
      site_url: fd.get("site_url") as string,
      brand: fd.get("brand") as string,
      audience_primary: fd.get("audience_primary") as string,
      audience_secondary: (fd.get("audience_secondary") as string) || undefined,
      main_offers: (fd.get("main_offers") as string) || undefined,
      geo_focus: (fd.get("geo_focus") as string) || undefined,
      usp_key: (fd.get("usp_key") as string) || undefined,
      business_size: fd.get("business_size") as string,
      monthly_budget: fd.get("monthly_budget") as string,
      analysis_depth: fd.get("analysis_depth") as "quick" | "standard" | "comprehensive",
      max_pages_to_scan: parseInt(fd.get("max_pages_to_scan") as string) || 50,
      max_competitors: parseInt(fd.get("max_competitors") as string) || 5,
    };

    try {
      const res = await startAnalysis(req);
      navigate(`/analysis/${res.job_id}/progress`);
    } catch (err) {
      if (err instanceof ApiError && err.status === 402) {
        const detail = err.data as Record<string, unknown>;
        setError(`Monthly limit reached (${detail.used}/${detail.limit}). Upgrade your plan to continue.`);
      } else {
        setError(err instanceof Error ? err.message : "Failed to start analysis");
      }
      setSubmitting(false);
    }
  };

  const inputClass = "w-full px-3 py-2.5 bg-surface2 border border-border rounded-lg text-text text-sm placeholder:text-text2/50 focus:outline-none focus:border-accent transition-colors";
  const labelClass = "block text-xs font-medium text-text2 mb-1.5";
  const selectClass = `${inputClass} appearance-none cursor-pointer`;

  return (
    <div className="max-w-2xl mx-auto px-5 py-8">
      <h1 className="text-2xl font-bold mb-2">New Analysis</h1>
      <p className="text-text2 text-sm mb-8">Enter your website details to generate a comprehensive GTM playbook.</p>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Core fields */}
        <div className="bg-surface border border-border rounded-xl p-6 space-y-4">
          <div>
            <label className={labelClass}>Website URL *</label>
            <input name="site_url" type="url" placeholder="https://yoursite.com" required className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>Brand Name *</label>
            <input name="brand" type="text" placeholder="Your Brand" required className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>Primary Audience *</label>
            <input name="audience_primary" type="text" placeholder="e.g. Solo developers building SaaS" required className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>Secondary Audience</label>
            <input name="audience_secondary" type="text" placeholder="Optional" className={inputClass} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>Business Size</label>
              <select name="business_size" defaultValue="Small Team (2-10)" className={selectClass}>
                <option>Solopreneur</option>
                <option>Small Team (2-10)</option>
                <option>Growing Business (11-50)</option>
                <option>Enterprise (50+)</option>
              </select>
            </div>
            <div>
              <label className={labelClass}>Monthly Budget</label>
              <select name="monthly_budget" defaultValue="$500-$2000" className={selectClass}>
                <option>{"< $500"}</option>
                <option>$500-$2000</option>
                <option>$2000-$5000</option>
                <option>$5000-$10000</option>
                <option>{"> $10000"}</option>
              </select>
            </div>
          </div>
          <div>
            <label className={labelClass}>Analysis Depth</label>
            <select name="analysis_depth" defaultValue="comprehensive" className={selectClass}>
              <option value="quick">Quick (~3 min)</option>
              <option value="standard">Standard (~5 min)</option>
              <option value="comprehensive">Comprehensive (~8 min)</option>
            </select>
          </div>
        </div>

        {/* Advanced options */}
        <div className="bg-surface border border-border rounded-xl overflow-hidden">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="w-full px-6 py-4 text-left text-sm font-medium text-text2 hover:text-text flex items-center gap-2 transition-colors"
          >
            <span className={`transition-transform ${showAdvanced ? "rotate-90" : ""}`}>&#9654;</span>
            Advanced Options
          </button>
          {showAdvanced && (
            <div className="px-6 pb-6 space-y-4 border-t border-border pt-4">
              <div>
                <label className={labelClass}>Main Offers</label>
                <input name="main_offers" type="text" placeholder="Your key products/services" className={inputClass} />
              </div>
              <div>
                <label className={labelClass}>Geo Focus</label>
                <input name="geo_focus" type="text" defaultValue="global" className={inputClass} />
              </div>
              <div>
                <label className={labelClass}>Key USP</label>
                <input name="usp_key" type="text" placeholder="What makes you different" className={inputClass} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className={labelClass}>Max Pages</label>
                  <input name="max_pages_to_scan" type="number" defaultValue={50} min={1} max={200} className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>Max Competitors</label>
                  <input name="max_competitors" type="number" defaultValue={5} min={1} max={10} className={inputClass} />
                </div>
              </div>
            </div>
          )}
        </div>

        {error && (
          <div className="bg-danger/10 border border-danger/30 rounded-lg px-4 py-3 text-sm text-danger">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={submitting}
          className="w-full py-3 bg-accent hover:bg-accent2 disabled:opacity-50 text-white font-semibold rounded-lg transition-colors text-sm"
        >
          {submitting ? "Starting Analysis..." : "Run Analysis"}
        </button>
      </form>
    </div>
  );
}
