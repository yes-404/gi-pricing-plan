import { request } from "./client";
import type { components } from "./generated/schema";
import type { components as requestComponents } from "./generated/schema.requests";

export type ScoringResult = components["schemas"]["ScoringResult"];
export type LadderRung = components["schemas"]["LadderRung"];
export type Trace = components["schemas"]["Trace"];
export type TraceStep = components["schemas"]["TraceStep"];
/** The request body: the permissive generated set, since `options.trace` defaults (FR-251). */
export type QuoteContext = requestComponents["schemas"]["QuoteContext"];
export type QuotePurpose = QuoteContext["purpose"];
export type ScoreComparison = components["schemas"]["ScoreComparison"];
export type StepChange = components["schemas"]["StepChange"];
/** The request body: the permissive generated set, as for QuoteContext. */
export type ScoreCompareRequest = requestComponents["schemas"]["ScoreCompareRequest"];

/**
 * Score one quote against an explicit Rating Version (03 FR-251, `POST /api/v1/score`).
 *
 * A decline is a **successful** response with `outcome: "declined"` (FR-256), so it resolves
 * here and is never a `ProblemError`; only the typed per-quote errors of FR-255 reject.
 */
export function scoreQuote(body: QuoteContext, signal?: AbortSignal): Promise<ScoringResult> {
  return request<ScoringResult>("/score", {
    method: "POST",
    body,
    ...(signal ? { signal } : {}),
  });
}

/**
 * Score one quote against two Rating Versions with a step-level trace diff (03 FR-262,
 * `POST /api/v1/score/compare`). `context` never carries `options.rating_version_ref`: the
 * route refuses it with 422, because `base` and `comparison` name the versions (03:1060).
 * A per-quote error on either side rejects with a `ProblemError` whose detail names the side.
 */
export function scoreCompare(
  body: ScoreCompareRequest,
  signal?: AbortSignal,
): Promise<ScoreComparison> {
  return request<ScoreComparison>("/score/compare", {
    method: "POST",
    body,
    ...(signal ? { signal } : {}),
  });
}
