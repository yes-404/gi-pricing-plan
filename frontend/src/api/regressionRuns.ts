import { request } from "./client";
import type { components } from "./generated/schema";
import { pageThrough, type Paged } from "./paging";

export type RegressionRun = components["schemas"]["RegressionRun"];
export type RegressionRunSummary = components["schemas"]["RegressionRunSummary"];
export type GoldenQuoteResult = components["schemas"]["GoldenQuoteResult"];
export type PropertyResult = components["schemas"]["PropertyResult"];

/**
 * How many pages `listRegressionRuns` will fetch before it stops and says so (FR-1932).
 * Ten pages of the server's `MAX_LIMIT` is two thousand runs of one Rating Version, far past
 * what a picker can usefully show; past it the result is `truncated`, newest first, so the
 * runs a pricing actuary wants are the ones kept.
 */
export const REGRESSION_RUN_PAGE_CAP = 10;

/** `GET /rating-versions/{id}/regression-runs`, newest first (`03` §5.1). */
export function listRegressionRuns(ratingVersionId: string): Promise<Paged<RegressionRunSummary>> {
  return pageThrough<RegressionRunSummary>(
    `/rating-versions/${encodeURIComponent(ratingVersionId)}/regression-runs`,
    {},
    REGRESSION_RUN_PAGE_CAP,
  );
}

/** One run by id — `rating:read`, workspace-scoped (FR-1221). Never the case log. */
export function getRegressionRun(ratingVersionId: string, runId: string): Promise<RegressionRun> {
  return request<RegressionRun>(
    `/rating-versions/${encodeURIComponent(ratingVersionId)}/regression-runs/${encodeURIComponent(runId)}`,
  );
}
