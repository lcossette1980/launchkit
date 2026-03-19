import { get, post } from "./client";
import type { BillingStatus } from "../types/api";

export const getBillingStatus = () => get<BillingStatus>("/billing/status");

export const createCheckout = (plan: "pro" | "agency") =>
  post<{ checkout_url: string }>("/billing/checkout", { plan });

export const getPortalUrl = () =>
  get<{ portal_url: string }>("/billing/portal");

export const syncBilling = () =>
  post<{ plan: string; synced: boolean }>("/billing/sync", {});
