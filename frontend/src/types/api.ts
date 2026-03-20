// ---- Auth ----
export interface User {
  id: string;
  email: string;
  name: string;
  plan: "free" | "pro" | "agency";
  email_verified: boolean;
  is_admin?: boolean;
}

export interface LoginResponse {
  message: string;
  is_new: boolean;
}

// ---- Analysis ----
export type JobStatus = "pending" | "running" | "completed" | "failed";

export interface JobCreatedResponse {
  job_id: string;
  status: string;
}

export interface JobStatusResponse {
  job_id: string;
  status: JobStatus;
  progress_pct: number;
  current_step: string;
  brand: string;
  site_url: string;
  error_message: string | null;
}

export interface JobListItem {
  job_id: string;
  status: JobStatus;
  brand: string;
  site_url: string;
  progress_pct: number;
  created_at: string | null;
  completed_at: string | null;
}

export interface AnalysisRequest {
  site_url: string;
  brand: string;
  audience_primary: string;
  audience_secondary?: string;
  main_offers?: string;
  geo_focus?: string;
  usp_key?: string;
  business_size?: string;
  monthly_budget?: string;
  analysis_depth?: "quick" | "standard" | "comprehensive";
  max_pages_to_scan?: number;
  max_competitors?: number;
}

// ---- Report / Results ----
export interface Scores {
  clarity: number;
  audience_fit: number;
  conversion: number;
  seo: number;
  ux: number;
}

export interface PageAnalysis {
  url: string;
  title: string;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  scores: Scores;
  quick_wins: string[];
}

export interface WebsiteAnalysis {
  pages_analyzed?: PageAnalysis[];
  overall_scores?: Scores | null;
  top_strengths?: string[];
  top_weaknesses?: string[];
  top_recommendations?: string[];
  quick_wins?: string[];
  crawl_failed?: boolean;
  crawl_errors?: string[];
}

export interface ExecutiveSummary {
  overview?: string;
  key_findings?: string[];
  top_priorities?: string[];
}

export interface MarketResearch {
  trends?: string[];
  target_audience?: string;
  competitive_landscape?: string;
  keyword_opportunities?: string[];
  content_topics?: string[];
}

export interface Competitor {
  url: string;
  name: string;
  value_proposition?: string;
  target_audience?: string;
  pricing_model?: string;
  key_differentiators?: string[];
  strengths?: string[];
  weaknesses?: string[];
  content_strategy?: string;
}

export interface Channels {
  primary?: string[];
  secondary?: string[];
}

export interface ImplementationRoadmap {
  "30_day"?: string[];
  "60_day"?: string[];
  "90_day"?: string[];
}

export interface GTMStrategy {
  positioning?: string[];
  channels?: Channels;
  content_strategy?: string[];
  partnerships?: string[];
  pricing?: string[];
  quick_wins?: string[];
  implementation_roadmap?: ImplementationRoadmap;
}

export interface Headline {
  headline: string;
  subheadline?: string;
  cta?: string;
}

export interface EmailTemplate {
  subject: string;
  body: string;
}

export interface LandingPageSections {
  problem?: string[];
  solution?: string[];
  benefits?: string[];
  social_proof?: string[];
  faq?: string[];
}

export interface CopyKit {
  headlines?: Headline[];
  value_propositions?: string[];
  emails?: Record<string, EmailTemplate>;
  linkedin_messages?: Record<string, string>;
  ads?: Record<string, { headline: string; description: string; cta?: string }>;
  landing_page_sections?: LandingPageSections;
}

export interface Alert {
  metric: string;
  threshold: string;
  action: string;
}

export interface DashboardSpec {
  north_star_metric?: string;
  north_star_target?: string;
  primary_kpis?: string[];
  secondary_metrics?: string[];
  cadence?: { daily?: string[]; weekly?: string[]; monthly?: string[] };
  alerts?: Alert[];
}

export interface BrandInfo {
  brand: string;
  url: string;
  audience_primary?: string;
  audience_secondary?: string;
  main_offers?: string;
  usp_key?: string;
  business_size?: string;
  monthly_budget?: string;
}

export interface AnalysisMetadata {
  job_id: string;
  analysis_depth?: string;
  pages_crawled?: number;
  competitors_analyzed?: number;
  completed_at?: string | null;
}

export interface FullReport {
  brand_info?: BrandInfo;
  executive_summary?: ExecutiveSummary;
  website_analysis?: WebsiteAnalysis;
  market_research?: MarketResearch;
  competitor_analysis?: { competitors?: Competitor[] };
  gtm_strategy?: GTMStrategy;
  experiments?: { experiments?: Array<Record<string, unknown>> };
  copy_kit?: CopyKit;
  dashboard?: DashboardSpec;
  metadata?: AnalysisMetadata;
  _teaser?: boolean;
}

// ---- Billing ----
export interface BillingStatus {
  plan: string;
  has_subscription: boolean;
  subscription_status: string | null;
  current_period_end: string | null;
  cancel_at_period_end: boolean;
}

// ---- API Keys ----
export interface ApiKey {
  key_id: string;
  name: string;
  is_active: boolean;
  last_used_at: string | null;
  created_at: string | null;
}
