import { Link, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const NAV_ITEMS = [
  { path: "/dashboard", label: "Dashboard" },
  { path: "/new", label: "New Analysis" },
  { path: "/pricing", label: "Pricing" },
  { path: "/settings", label: "Settings" },
];

const PLAN_COLORS: Record<string, string> = {
  free: "bg-border text-text2",
  pro: "bg-accent/15 text-accent2",
  agency: "bg-success/15 text-success",
};

export default function AppShell() {
  const { user, logout } = useAuth();
  const location = useLocation();

  return (
    <div className="min-h-screen flex flex-col">
      {/* Nav */}
      <nav className="border-b border-border bg-surface/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-5 flex items-center justify-between h-14">
          <div className="flex items-center gap-8">
            <Link to="/dashboard" className="text-lg font-bold tracking-tight">
              <span className="text-accent2">VC</span>
              <span className="text-text">LaunchKit</span>
            </Link>
            <div className="hidden md:flex items-center gap-1">
              {NAV_ITEMS.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    location.pathname === item.path
                      ? "bg-accent/15 text-accent2"
                      : "text-text2 hover:text-text hover:bg-surface2"
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </div>

          {user && (
            <div className="flex items-center gap-3">
              <span className="text-xs text-text2 hidden sm:block max-w-[160px] truncate">
                {user.email}
              </span>
              <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${PLAN_COLORS[user.plan] ?? PLAN_COLORS.free}`}>
                {user.plan}
              </span>
              <button
                onClick={logout}
                className="text-xs text-text2 border border-border rounded px-2 py-1 hover:border-danger hover:text-danger transition-colors"
              >
                Log out
              </button>
            </div>
          )}
        </div>
      </nav>

      {/* Main content */}
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}
