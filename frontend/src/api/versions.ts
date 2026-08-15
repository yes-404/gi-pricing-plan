import { request } from "./client";
import type { components } from "./generated/schema";

export type DatasetVersion = components["schemas"]["DatasetVersion"];
export type DatasetTable = components["schemas"]["DatasetTable"];
export type VersionTotals = components["schemas"]["VersionTotals"];

export interface RejectedRows {
  readonly rows_read: number;
  readonly rows_written: number;
  readonly rows_rejected: number;
  readonly reject_rate: number;
  readonly sample: readonly Record<string, unknown>[];
}

export function getVersion(slug: string, version: number): Promise<DatasetVersion> {
  return request<DatasetVersion>(`/datasets/${encodeURIComponent(slug)}/versions/${version}`);
}

/**
 * FR-DATA-7's quarantine. A **404 is an ordinary answer**, not a failure: a derived
 * version has no ingestion run of its own, and the caller should say so rather than show
 * an error.
 */
export function getRejected(versionId: string): Promise<RejectedRows> {
  return request<RejectedRows>(`/dataset-versions/${versionId}/rejected`);
}

/**
 * Format an exact decimal for display **without parsing it**.
 *
 * `exposure_years` is a string because a JS number is a float64 (FR-OVR-7). Grouping the
 * integer part is presentation; `parseFloat` would be arithmetic, and arithmetic on a
 * value the backend already computed exactly is how a total stops matching the report
 * that cites it.
 */
export function formatDecimalString(value: string, maximumFractionDigits = 2): string {
  const [whole = "0", fraction = ""] = value.split(".");
  const sign = whole.startsWith("-") ? "-" : "";
  const digits = sign ? whole.slice(1) : whole;
  const grouped = digits.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  const trimmed = fraction.slice(0, maximumFractionDigits).replace(/0+$/, "");
  return trimmed ? `${sign}${grouped}.${trimmed}` : `${sign}${grouped}`;
}

/**
 * Money, from integer minor units. Divides by 100 for display only — the value crossing
 * the wire stays an integer count of pence or cents, which is what makes it exact.
 */
export function formatMinor(minor: number, currency: string): string {
  return new Intl.NumberFormat(undefined, { style: "currency", currency }).format(minor / 100);
}
