import { gbmSpec, type Model } from "@/api/models";

/**
 * A fitted LightGBM, annotated rather than cast.
 *
 * The annotation is the point: `as unknown as Model` would let `GbmFitResult` drift in the
 * generated contract without a single test noticing, which is the failure FR-OVR-6 exists to
 * prevent. Annotated, drift fails `pnpm test` rather than review.
 *
 * `lightgbm` and not `xgboost` on purpose — `02` §4.4 (amended 2026-08-17) folded the old
 * `backend` field into `model_type`, so the second value is the one a narrower written from
 * memory forgets.
 */
export const GBM_MODEL: Model = {
  id: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
  model_family_slug: "motor-ad-frequency",
  version: 7,
  status: "fitted",
  spec_hash: "v10:sha256:abc",
  dataset_version_id: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
  spec: {
    model_type: "lightgbm",
    model_family_slug: "motor-ad-frequency",
    dataset_version_id: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
    response_column: "ad_claim_count",
    objective: { kind: "builtin", name: "count:poisson" },
    categorical_handling: "native",
    eval_metrics: [],
    factors: ["driver_age_banded"],
    interaction_constraints: [],
    loss_treatment: { kind: "none" },
    monotone_constraints: "derived_from_factors",
    offset: { kind: "log_column", column: "exposure_years" },
    weight: { kind: "none" },
    seed: 0,
    interval_for: null,
  },
  fit_result: {
    model_type: "lightgbm",
    booster_blob: { sha256: "a".repeat(64), bytes: 184320, media_type: "text/plain" },
    booster_format: "lightgbm_text",
    feature_order: ["driver_age_banded"],
    base_margin: { kind: "log_column", column: "exposure_years" },
    monotone_constraints: [1],
    dropped_eval_metrics: [],
    best_iteration: 184,
    fit_seconds: 41.7,
    rows: 413169,
    inverse_link: "exp",
    library_versions: { lightgbm: "4.5.0", polars: "1.35.0" },
  },
  flags: [],
};

/**
 * The same family refitted as a quantile bound of version 7 (FR-MODEL-78).
 *
 * Built through `gbmSpec` rather than by spreading `GBM_MODEL.spec`: that field is the
 * three-arm union, and spreading a union member produces a value assignable to none of the
 * arms under `exactOptionalPropertyTypes`. Going through the narrower keeps the annotation
 * doing its job instead of reaching for a cast to silence it.
 */
export function boundOf(alpha: number): Model {
  return {
    ...GBM_MODEL,
    id: "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
    version: 8,
    spec: {
      ...gbmSpec(GBM_MODEL)!,
      interval_for: {
        model_id: GBM_MODEL.id,
        model_version: GBM_MODEL.version,
        alpha,
      },
    },
  };
}
