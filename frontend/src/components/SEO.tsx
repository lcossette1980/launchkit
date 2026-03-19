import { Helmet } from "react-helmet-async";

interface SEOProps {
  title?: string;
  description?: string;
  path?: string;
  ogImage?: string;
}

const DEFAULTS = {
  siteName: "VCLaunchKit",
  title: "VCLaunchKit — From URL to GTM Strategy in 10 Minutes",
  description:
    "AI-powered GTM playbooks for solo developers and small teams. Crawl your site, benchmark competitors, get a page-by-page audit, copy kit, email templates, and 30/60/90 day roadmap.",
  url: "https://vclaunchkit.com",
  image: "https://vclaunchkit.com/og-image.png",
};

export default function SEO({ title, description, path = "", ogImage }: SEOProps) {
  const fullTitle = title ? `${title} | VCLaunchKit` : DEFAULTS.title;
  const desc = description || DEFAULTS.description;
  const url = `${DEFAULTS.url}${path}`;
  const image = ogImage || DEFAULTS.image;

  return (
    <Helmet>
      <title>{fullTitle}</title>
      <meta name="description" content={desc} />
      <link rel="canonical" href={url} />

      <meta property="og:type" content="website" />
      <meta property="og:site_name" content={DEFAULTS.siteName} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={desc} />
      <meta property="og:url" content={url} />
      <meta property="og:image" content={image} />

      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={desc} />
      <meta name="twitter:image" content={image} />
    </Helmet>
  );
}
