import { request } from "./client";
import type { components } from "./generated/schema";

export type ValidationReport = components["schemas"]["ValidationReport"];
export type RuleResult = components["schemas"]["RuleResult"];
export type ReportSummary = components["schemas"]["ReportSummary"];
export type DatasetVersion = components["schemas"]["DatasetVersion"];
export type ValidationLayer = components["schemas"]["ValidationLayer"];
export type RuleOutcome = components["schemas"]["RuleOutcome"];

/** `01` §5.1 — resolve a slug and version number to the version itself. */
export function getVersion(slug: string, version: number): Promise<DatasetVersion> {
  return request<DatasetVersion>(`/datasets/${encodeURIComponent(slug)}/versions/${version}`);
}

/** Report history, newest first. Summaries only — no bodies (NFR-471). */
export function listReports(versionId: string): Promise<ReportSummary[]> {
  return request<ReportSummary[]>(`/dataset-versions/${versionId}/validation-reports`);
}

/** The full report, with its acknowledgements merged in. */
export function getReport(reportId: string): Promise<ValidationReport> {
  return request<ValidationReport>(`/validation-reports/${reportId}`);
}

/**
 * Acknowledge one warning (FR-46).
 *
 * The justification is not optional and not a formality — it is the audit record, and the
 * platform refuses an empty one. Pricing Actuary role only; anything else comes back
 * `ACKNOWLEDGE_FORBIDDEN_ROLE`, which is a different message to the user than a generic
 * permission failure: go and find an actuary, not go and ask for a grant.
 */
export function acknowledge(
  reportId: string,
  ruleId: string,
  justification: string,
): Promise<unknown> {
  return request(`/validation-reports/${reportId}/results/${ruleId}/acknowledge`, {
    method: "POST",
    body: { justification },
  });
}

/**
 * The order `01` §5.3 requires: **overall banner → failing rules → warnings needing
 * acknowledgement → everything else**, answerable without scrolling past the fold.
 *
 * The spec also describes "four layer sections". The two are reconciled by letting urgency
 * win at the top and layers organise the tail: a reader asking "why can I not fit a model
 * on this?" needs the blocking rules first, and a failing structural rule and a failing
 * actuarial one are equally blocking. Layers group the rules nobody has to act on.
 */
export const BANDS = ["blocking", "needs-acknowledgement", "acknowledged", "other"] as const;
export type Band = (typeof BANDS)[number];

export function bandOf(result: RuleResult): Band {
  if (result.outcome === "fail" || result.outcome === "error") return "blocking";
  if (result.outcome === "warn") {
    return result.acknowledgement ? "acknowledged" : "needs-acknowledgement";
  }
  return "other";
}

export function groupIntoBands(report: ValidationReport): Record<Band, RuleResult[]> {
  const bands: Record<Band, RuleResult[]> = {
    blocking: [],
    "needs-acknowledgement": [],
    acknowledged: [],
    other: [],
  };
  for (const result of report.results ?? []) bands[bandOf(result)].push(result);
  return bands;
}

/**
 * Whether this report permits promotion to `validated` (`01` §1.3, FR-46).
 *
 * Computed from the same two facts the backend uses — no fails or errors, and every
 * warning acknowledged — so the banner cannot claim a version is ready when the platform
 * would refuse it. The platform is still the authority; this only decides what to show.
 */
export function blocksModelling(report: ValidationReport): boolean {
  const bands = groupIntoBands(report);
  return bands.blocking.length > 0 || bands["needs-acknowledgement"].length > 0;
}
