import type { ModelComparison } from "@/api/comparisons";
import { gbmSpec, type Model, type TransparencyArtifact } from "@/api/models";

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
 * A transparency artifact for `GBM_MODEL` (FR-MODEL-33, FR-MODEL-34).
 *
 * Carries the GLM-approximation and SHAP blocks but not `ebm_shape_functions`: the three are
 * independently optional, and a fixture with all three present would let a panel that renders
 * a block unconditionally pass.
 */
export const ARTIFACT: TransparencyArtifact = {
  id: "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee",
  model_id: GBM_MODEL.id,
  created_at: "2026-08-20T09:14:00Z",
  fidelity_statement:
    "The GLM approximation reproduces the booster to within 3 % of predicted frequency over " +
    "96 % of exposure. It will under-price young drivers on high-value vehicles, where the " +
    "booster's interaction is not representable in the additive table.",
  monotonicity_verified: true,
  glm_approximation: {
    target: "gbm_prediction",
    family: "gamma",
    link: "log",
    r_squared: 0.964,
    deviance_explained: 0.951,
    approximating_model_id: "ffffffff-ffff-4fff-8fff-ffffffffffff",
    coefficients: [],
    relativities: {},
    worst_regions: [
      {
        description: "driver_age_banded = 17–21 and vehicle_group_rated ≥ 40",
        exposure_share: 0.008,
        mean_abs_error_pct: 11.4,
      },
      {
        description: "annual_mileage ≥ 25000",
        exposure_share: 0.031,
        mean_abs_error_pct: 6.2,
      },
    ],
  },
  shap_summary: {
    algorithm: "tree_shap",
    sample_rows: 20000,
    seed: 7,
    interactions_available: true,
    mean_abs_contribution: [
      { factor: "driver_age_banded", value: 0.148 },
      { factor: "vehicle_group_rated", value: 0.092 },
    ],
    top_interactions: [{ pair: ["driver_age_banded", "vehicle_group_rated"], strength: 0.031 }],
  },
};

/**
 * A fitted EBM, annotated for the same reason `GBM_MODEL` is.
 *
 * One numeric term and one categorical, because the slot layout differs between them: `c`
 * cuts give `c + 3` slots and `L` levels give `L + 2`, and a fixture carrying only one kind
 * lets the other's off-by-one through.
 */
export const EBM_MODEL: Model = {
  id: "dddddddd-dddd-4ddd-8ddd-dddddddddddd",
  model_family_slug: "motor-severity",
  version: 3,
  status: "fitted",
  spec_hash: "v10:sha256:def",
  dataset_version_id: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
  spec: {
    model_type: "ebm",
    model_family_slug: "motor-severity",
    dataset_version_id: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
    response_column: "claim_amount",
    objective: "rmse",
    max_bins: 64,
    max_rounds: 50000,
    interactions: 0,
    factors: [],
    offset: { kind: "none" },
    weight: { kind: "none" },
    loss_treatment: { kind: "none" },
    seed: 0,
  },
  fit_result: {
    model_type: "ebm",
    objective: "rmse",
    link: "identity",
    intercept: 6.8142,
    feature_order: ["annual_mileage", "region_grouped"],
    bins: [
      { kind: "numeric", cuts: [5000, 10000, 20000] },
      { kind: "categorical", levels: ["north", "midlands", "south"] },
    ],
    terms: [
      {
        term_name: "annual_mileage",
        term_features: [0],
        scores: [0.0, -0.11, -0.02, 0.07, 0.19, 0.0],
        standard_deviations: [0.0, 0.008, 0.006, 0.005, 0.007, 0.0],
        bin_weights: [0.0, 38214.4, 52110.8, 60452.1, 33489.0, 0.0],
      },
      {
        term_name: "region_grouped",
        term_features: [1],
        scores: [0.0, 0.04, -0.01, 0.02, 0.0],
        standard_deviations: [0.0, 0.003, 0.002, 0.003, 0.0],
        bin_weights: [0.0, 120000.0, 90000.0, 41000.0, 0.0],
      },
    ],
    best_iteration: 412,
    rows: 480000,
    fit_seconds: 92.4,
    library_versions: { "interpret-core": "0.7.8" },
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

/**
 * `02` §4.11's own example, transcribed. The spec writes the large integers with numeric
 * separators (`169_503`); they are written plainly here because the two forms are equal in
 * TypeScript and a reader diffing this against the spec should not have to check that.
 */
export const COMPARISON: ModelComparison = {
  id: "5c1b0e6a-7777-4888-8999-aaaabbbbcccc",
  computed_at: "2026-08-17T15:20:11Z",
  job_id: "1a2b3c4d-5555-4666-8777-888899990000",
  summary: {
    model_refs: ["model:motor-ad-frequency@7", "model:motor-ad-frequency-gbm@2"],
    baseline_ref: "model:motor-ad-frequency@7",
    split_ref: {
      split_artifact_id: "9f8e7d6c-1111-4222-8333-444455556666",
      train_part: "train",
      holdout_part: "test",
    },
    holdout_rows: 169503,
    metrics: [
      {
        metric: "gini_normalised",
        weighting: "exposure",
        direction: "higher_is_better",
        values: [
          { model_ref: "model:motor-ad-frequency@7", value: 0.412 },
          { model_ref: "model:motor-ad-frequency-gbm@2", value: 0.43 },
        ],
        leader: "model:motor-ad-frequency-gbm@2",
      },
      {
        metric: "ae_overall",
        weighting: "exposure",
        direction: "closer_to_one_is_better",
        values: [
          { model_ref: "model:motor-ad-frequency@7", value: 1.001 },
          { model_ref: "model:motor-ad-frequency-gbm@2", value: 0.994 },
        ],
        leader: "model:motor-ad-frequency@7",
      },
    ],
    double_lift: [
      {
        baseline_ref: "model:motor-ad-frequency@7",
        challenger_ref: "model:motor-ad-frequency-gbm@2",
        weighting: "exposure",
        bins: [
          {
            bin: 1,
            rows: 16950,
            actual: 0.0491,
            baseline_predicted: 0.0523,
            challenger_predicted: 0.0447,
            exposure_years: "14203.400000",
          },
        ],
      },
    ],
    relativity_differences: [
      {
        factor: "driver_age_banded",
        level: "17-20",
        values: [
          { model_ref: "model:motor-ad-frequency@7", value: 1.718 },
          { model_ref: "model:motor-ad-frequency-gbm@2", value: 1.902 },
        ],
        max_abs_difference: 0.184,
      },
    ],
  },
};
