import { request } from "./client";
import type { components } from "./generated/schema";

export type DatasetVersion = components["schemas"]["DatasetVersion"];
export type DatasetSplit = components["schemas"]["DatasetSplit"];
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
 * The same version by its own id — the resource `01` §5.1's nine `/dataset-versions/{id}/…`
 * routes hang off, and which the table did not declare until 2026-08-15.
 *
 * A view routed on a version id and not a dataset slug has no other way to reach it. The
 * factor workbench is exactly that: `/factors/:datasetVersionId`, needing the `dataset_id`
 * a Banding is keyed to.
 */
/**
 * The splits defined on a Dataset Version (`01` FR-76).
 *
 * The model spec builder's split picker reads these: `SplitRef` names a split artifact and
 * two of its `parts`, and a version with no split is a version whose models have no
 * holdout. Listed rather than derived — FR-76 records the split on the parent version
 * precisely so "trained on the same split" is one artifact two models cite.
 */
export function listSplits(versionId: string): Promise<DatasetSplit[]> {
  return request<DatasetSplit[]>(
    `/dataset-versions/${encodeURIComponent(versionId)}/splits`,
  );
}

export function getVersionById(versionId: string): Promise<DatasetVersion> {
  return request<DatasetVersion>(`/dataset-versions/${versionId}`);
}

/**
 * FR-32's quarantine. A **404 is an ordinary answer**, not a failure: a derived
 * version has no ingestion run of its own, and the caller should say so rather than show
 * an error.
 */
export function getRejected(versionId: string): Promise<RejectedRows> {
  return request<RejectedRows>(`/dataset-versions/${versionId}/rejected`);
}

/**
 * Format an exact decimal for display **without parsing it**.
 *
 * `exposure_years` is a string because a JS number is a float64 (FR-10). Grouping the
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
