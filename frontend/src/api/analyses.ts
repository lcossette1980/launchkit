import { get, post, del } from "./client";
import type { AnalysisRequest, FullReport, JobCreatedResponse, JobListItem, JobStatusResponse } from "../types/api";

export const listAnalyses = (limit = 20, offset = 0) =>
  get<JobListItem[]>(`/analyses?limit=${limit}&offset=${offset}`);

export const getAnalysis = (id: string) => get<FullReport>(`/analyses/${id}`);

export const getAnalysisStatus = (id: string) => get<JobStatusResponse>(`/analyses/${id}/status`);

export const startAnalysis = (req: AnalysisRequest) =>
  post<JobCreatedResponse>("/analyses", req);

export const rerunAnalysis = (id: string) =>
  post<JobCreatedResponse>(`/analyses/${id}/rerun`);

export const getReportUrl = (id: string, format: "json" | "html" | "pdf") =>
  `/api/v1/analyses/${id}/report/${format}`;

// Share link management
export const createShareLink = (id: string) =>
  post<{ share_token: string; share_url: string; is_public: boolean }>(`/analyses/${id}/share`);

export const revokeShareLink = (id: string) =>
  del<{ is_public: boolean }>(`/analyses/${id}/share`);

export const getShareInfo = (id: string) =>
  get<{ is_public: boolean; share_token: string | null; share_url: string | null }>(`/analyses/${id}/share-info`);

// Public shared report (no auth)
export const getSharedReport = (token: string) =>
  get<{ brand: string; site_url: string; completed_at: string | null; results: FullReport; _shared: boolean }>(`/share/${token}`);
