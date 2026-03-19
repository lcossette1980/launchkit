import { Link } from "react-router-dom";
import SEO from "../components/SEO";

export default function NotFoundPage() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <SEO title="Page Not Found" description="The page you're looking for doesn't exist." />
      <div className="text-center">
        <p className="text-5xl font-bold text-accent2 mb-2">404</p>
        <p className="text-text2 mb-6">Page not found</p>
        <Link to="/" className="px-5 py-2.5 bg-accent text-white font-semibold rounded-lg text-sm">
          Go Home
        </Link>
      </div>
    </div>
  );
}
