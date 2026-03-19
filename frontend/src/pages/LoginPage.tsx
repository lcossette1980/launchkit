import { useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const { user, login } = useAuth();
  const [email, setEmail] = useState("");
  const [sending, setSending] = useState(false);
  const [message, setMessage] = useState<{ text: string; isError: boolean } | null>(null);

  if (user) return <Navigate to="/dashboard" replace />;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSending(true);
    setMessage(null);
    try {
      await login(email);
      setMessage({ text: "Check your email (or terminal logs) for the magic link!", isError: false });
    } catch (err) {
      setMessage({ text: err instanceof Error ? err.message : "Failed to send", isError: true });
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg px-4">
      <div className="bg-surface border border-border rounded-2xl p-10 max-w-md w-full text-center">
        <h1 className="text-2xl font-bold mb-1">
          <span className="text-accent2">VC</span>LaunchKit
        </h1>
        <p className="text-text2 text-sm mb-8">AI-Powered GTM Playbooks for Builders</p>

        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
            className="w-full px-4 py-3 bg-surface2 border border-border rounded-lg text-text placeholder:text-text2/50 focus:outline-none focus:border-accent transition-colors"
          />
          <button
            type="submit"
            disabled={sending}
            className="w-full py-3 bg-accent hover:bg-accent2 disabled:opacity-50 text-white font-semibold rounded-lg transition-colors"
          >
            {sending ? "Sending..." : "Send Magic Link"}
          </button>
        </form>

        {message && (
          <p className={`mt-4 text-sm ${message.isError ? "text-danger" : "text-success"}`}>
            {message.text}
          </p>
        )}
      </div>
    </div>
  );
}
