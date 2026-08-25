import { request } from "./client";
import type { components } from "./generated/schema";

export type Prediction = components["schemas"]["Prediction"];
export type PredictedRow = components["schemas"]["PredictedRow"];
export type Uncertainty = components["schemas"]["Uncertainty"];
export type UncertaintyKind = components["schemas"]["UncertaintyKind"];
export type UncertaintyBasis = components["schemas"]["UncertaintyBasis"];
export type UnavailableReason = components["schemas"]["UnavailableReason"];
export type IntervalModels = components["schemas"]["IntervalModels"];

/** One row of caller-supplied column values. `PredictRows.rows` items are open objects. */
export type PredictionInputRow = Record<string, string | number | boolean | null>;

/**
 * Score one row (`02` §5.1, FR-MODEL-63).
 *
 * **200, not 202.** The §5.1 row for this endpoint states the code directly, and `07` §1.3 R1
 * explains why that is not an exception to "everything slow is a Job": the endpoint reads at
 * most `MAX_PREDICT_ROWS` rows the caller sent in the body, so it cannot exceed R1's 2 s
 * threshold. There is no Job, no poll and no result blob — the response is the answer.
 *
 * No `Idempotency-Key`. `00` §5.4 asks for one on "every POST that creates a Job or artifact";
 * this creates neither, and a retried score is the same arithmetic on the same numbers.
 */
export function predict(modelId: string, row: PredictionInputRow): Promise<Prediction> {
  return request<Prediction>(`/models/${encodeURIComponent(modelId)}/predict`, {
    method: "POST",
    body: { rows: [row] },
  });
}

/**
 * What an `unavailable` reason means, in the specification's own reading of it.
 *
 * `family` exists because FR-MODEL-93 is explicit that `covariance_not_stored` is "a fourth
 * reason beside FR-MODEL-77's three and it is **not** one of them", and FR-MODEL-124 is
 * explicit that each of the other four "states something false of an EBM". Grouping them in
 * the UI would undo both statements.
 */
export function unavailableCopy(reason: UnavailableReason): {
  family: "glm" | "gbm" | "ebm";
  headline: string;
  detail: string;
} {
  switch (reason) {
    case "no_interval_models_fitted":
      // FR-MODEL-77: paired quantile models are opt-in, at 2-3x fit cost (FR-MODEL-78).
      return {
        family: "gbm",
        headline: "No interval models were fitted",
        detail:
          "Interval bounds are opt-in for a boosted model: they are two more fits, at two "
          + "to three times the cost of this one. Until they exist there is no interval to "
          + "report, and an approximation is not offered in their place.",
      };
    case "interval_models_not_approved":
      // FR-MODEL-100(ii) — NOT "the bounds are unapproved".
      return {
        family: "gbm",
        headline: "The bounds are less advanced than this model",
        detail:
          "The interval bounds sit at an earlier lifecycle status than the model they "
          + "bound, so quoting them would put an unreviewed number beside a reviewed one. "
          + "Advance the bounds to at least this model's status.",
      };
    case "interval_models_stale":
      // FR-MODEL-100(iii) — the literal reading of FR-MODEL-77's "superseded version".
      return {
        family: "gbm",
        headline: "This model version has been superseded",
        detail:
          "A superseded model is still scoreable, and its bounds are still attached to it "
          + "— but the family has moved past this version, so the interval is not reported "
          + "without saying so.",
      };
    case "covariance_not_stored":
      // FR-MODEL-93. Note what this reason is NOT: a blob that should exist and does not is
      // a platform fault and surfaces as one. This is reachable only when the artifact
      // itself records no blob.
      return {
        family: "glm",
        headline: "This fit stored no covariance matrix",
        detail:
          "The interval is read off the covariance matrix, and this model was fitted "
          + "before that matrix was retained. The expectation below is unaffected; refit to "
          + "get an interval.",
      };
    case "model_type_has_no_interval":
      // FR-MODEL-124.
      return {
        family: "ebm",
        headline: "This model type offers no interval",
        detail:
          "An explainable boosting machine has neither a covariance matrix nor paired "
          + "quantile bounds, so none of the other reasons would be true of it. The "
          + "expectation below is a full answer for this model type.",
      };
  }
}

/**
 * What kind of claim an interval on this page is making.
 *
 * FR-MODEL-101 is the whole reason this function exists: a paired-quantile interval covers
 * `Y` itself while `confidence_interval_mean` covers `E[Y|x]`, and "a reader comparing a
 * GBM's bound with a GLM's must be able to see they are not the same kind of claim". The two
 * strings must stay visibly different.
 */
export function intervalClaim(kind: Exclude<UncertaintyKind, "unavailable">): string {
  switch (kind) {
    case "confidence_interval_mean":
      // FR-MODEL-98: exactly one confidence-side kind, and it is "never silently widened"
      // into a process-variance prediction interval.
      return "the average outcome for rows like this one";
    case "quantile_pair_interval":
      // FR-MODEL-101.
      return "an individual outcome for a row like this one";
  }
}
