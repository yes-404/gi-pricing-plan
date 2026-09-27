import { pageThrough, type Paged } from "./paging";
import type { components } from "./generated/schema";

export type CustomMetric = components["schemas"]["CustomMetric"];
export type MetricStatus = components["schemas"]["MetricStatus"];

/**
 * The objective library's cap, reused rather than re-derived.
 *
 * `GET /custom-metrics` filters by `status` and `slug` only — the same shape OQ-605
 * decided for objectives, for the same reason — so applicability filtering happens in the
 * client over a capped sweep, and `truncated` is how the screen says so. A second constant
 * with a second rationale would be two numbers to keep equal; there is one rule.
 */
export const METRIC_PAGE_CAP = 5;

export type MetricList = Paged<CustomMetric>;

export async function listMetrics(
  options: { status?: MetricStatus | undefined } = {},
): Promise<MetricList> {
  return pageThrough<CustomMetric>("/custom-metrics", { status: options.status }, METRIC_PAGE_CAP);
}
