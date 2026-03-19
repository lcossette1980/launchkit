import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

/**
 * Consistent navigation bar for all public pages
 * (Landing, Login, Pricing, Examples, Blog, Shared Reports).
 */
export default function PublicNav() {
  const { user } = useAuth();

  return (
    <nav className="border-b border-border/50 bg-bg/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-5 flex items-center justify-between h-14">
        <Link to={user ? "/dashboard" : "/"} className="text-lg font-bold tracking-tight">
          <span className="text-accent2">VC</span>LaunchKit
        </Link>
        <div className="flex items-center gap-5">
          <a href="/#how-it-works" className="text-sm text-text2 hover:text-text transition-colors hidden sm:block">
            How It Works
          </a>
          <Link to="/examples" className="text-sm text-text2 hover:text-text transition-colors hidden sm:block">
            Examples
          </Link>
          <Link to="/blog" className="text-sm text-text2 hover:text-text transition-colors hidden sm:block">
            Blog
          </Link>
          <Link to="/pricing" className="text-sm text-text2 hover:text-text transition-colors">
            Pricing
          </Link>
          {user ? (
            <Link
              to="/dashboard"
              className="px-4 py-1.5 bg-accent hover:bg-accent2 text-white text-sm font-semibold rounded-lg transition-colors"
            >
              Dashboard
            </Link>
          ) : (
            <Link
              to="/login"
              className="px-4 py-1.5 bg-accent hover:bg-accent2 text-white text-sm font-semibold rounded-lg transition-colors"
            >
              Sign In
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}
