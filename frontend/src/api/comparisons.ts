import { request } from "./client";
import type { components } from "./generated/schema";
import type { Job } from "./jobs";

export type ModelComparison = components["schemas"]["ModelComparison"];
export type ComparisonSummary = components["schemas"]["ComparisonSummary"];
export type ComparisonMetric = components["schemas"]["ComparisonMetric"];
export type ComparisonValue = components["schemas"]["ComparisonValue"];
export type DoubleLift = components["schemas"]["DoubleLift"];
export type DoubleLiftBin = components["schemas"]["DoubleLiftBin"];
export type RelativityDifference = components["schemas"]["RelativityDifference"];
export type MetricDirection = components["schemas"]["MetricDirection"];

/**
 * Start a comparison (FR-MODEL-56). **202 with a Job, not the artifact** — the comparison
 * reads the holdout and scores every candidate, which is work.
 *
 * Every comparability rule is answered by this call before a Job exists — two or more models,
 * all fitted, one shared split, a baseline among them — so a 409 here is a complete answer
 * and not a job that will fail later. `baseline_id` is deliberately not sent: it defaults to
 * the first id, and `model_ids` is already ordered "in the order the table should present
 * them", so ordering the ids is how a caller chooses the baseline.
 */
export function startComparison(modelIds: readonly string[]): Promise<Job> {
  return request<Job>("/models/compare", {
    method: "POST",
    body: { model_ids: modelIds },
  });
}

/** The stored artifact (`02` §5.1), by comparison id. */
export function getComparison(comparisonId: string): Promise<ModelComparison> {
  return request<ModelComparison>(`/models/comparisons/${encodeURIComponent(comparisonId)}`);
}

/** The prefix `model_handlers.py:786` writes. Not `comparison:`, and not an ID-3 ref. */
const COMPARISON_REF = "model_comparison:";

/**
 * The comparison id a succeeded Job produced, or null.
 *
 * `JobResult.ref` is `{entity}:{uuid}` — a namespace of its own, not the ID-3
 * `{type}:{slug}@{version}` that `ComparisonValue.model_ref` carries. `model_comparison` is
 * not even a member of `refs.py`'s `ARTIFACT_TYPES`. The prefix is matched in full because a
 * looser check would also accept `model:{uuid}`, which a fit job emits.
 */
export function comparisonIdFromJob(job: Job): string | null {
  const ref = job.result?.ref;
  if (typeof ref !== "string" || !ref.startsWith(COMPARISON_REF)) return null;
  const id = ref.slice(COMPARISON_REF.length);
  return id.length > 0 ? id : null;
}

/**
 * `refs.py:30-43`'s `ModelRef` pattern, restated here because the frontend has no access to
 * the Python type and `ComparisonValue.model_ref` is published as an unconstrained string.
 * Kept character-for-character: slug is `[a-z0-9][a-z0-9-]{1,62}`, version `[1-9][0-9]*`.
 */
const MODEL_REF = /^model:([a-z0-9][a-z0-9-]{1,62})@([1-9][0-9]*)$/;

/**
 * Split an ID-3 model ref, or null when it does not parse.
 *
 * Null is a real outcome, not a defensive branch: `comparison.py` never imports `refs`, and
 * its four validators constrain only referential integrity inside the artifact. A caller
 * renders the raw string in that case rather than dropping it.
 */
export function parseModelRef(ref: string): { slug: string; version: number } | null {
  const match = MODEL_REF.exec(ref);
  return match === null ? null : { slug: match[1]!, version: Number(match[2]) };
}

/**
 * How one model stands on one metric.
 *
 * `02` §4.11 makes a null `leader` mean two different things — "the metric does not order"
 * **or** "the models tie", since "a winner chosen by tie-break is one the data did not
 * choose". `direction` is what separates them, and the view must show both.
 */
export function leaderState(
  metric: ComparisonMetric,
  modelRef: string,
): "leader" | "tied" | "unranked" | "behind" {
  if (metric.direction === "not_ordered") return "unranked";
  if (metric.leader === null || metric.leader === undefined) return "tied";
  return metric.leader === modelRef ? "leader" : "behind";
}
