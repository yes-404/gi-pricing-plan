import type { Diagnostics } from "@/api/diagnostics";
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

/**
 * A `Diagnostics` artifact with every arm populated — the GBM case, because it is the only
 * one that exercises both partitioned surfaces (`universal`, and `eval_curve` inside `gbm`).
 * Tests that need an arm absent set it to `null` on a spread of this constant rather than
 * declaring a second fixture, so there is one place where the shape is written down.
 *
 * The numbers are small and made up. They are not a fit of anything; the only property any
 * test relies on is that train and holdout differ, so a chart plotting one twice fails.
 */
export const DIAGNOSTICS: Diagnostics = {
  id: "33333333-3333-4333-8333-333333333333",
  model_id: GBM_MODEL.id,
  computed_at: "2026-08-24T09:00:00Z",
  job_id: "44444444-4444-4444-8444-444444444444",
  universal: {
    train: {
      weighting: "exposure",
      rows: 407_530,
      ae_overall: 1.002,
      ae_by_factor: [
        { factor: "vehicle_age", level: "0-3", actual: 0.061, expected: 0.059, ae: 1.034,
          exposure_years: "12034.5" },
        { factor: "vehicle_age", level: "4-9", actual: 0.048, expected: 0.05, ae: 0.96,
          exposure_years: "20115.25" },
      ],
      lift: [
        { bin: 1, rows: 40_753, predicted: 0.021, actual: 0.023, exposure_years: "3210.5" },
        { bin: 2, rows: 40_753, predicted: 0.049, actual: 0.047, exposure_years: "3199.0" },
      ],
      gini: 0.312,
      gini_normalised: 0.418,
      calibration: [
        { bin: 1, rows: 40_753, predicted: 0.021, actual: 0.023 },
        { bin: 2, rows: 40_753, predicted: 0.049, actual: 0.047 },
      ],
      residual_summary: {
        mean: 0.0004, std: 0.212, minimum: -1.88, maximum: 9.42, p01: -0.55, p99: 0.71,
      },
    },
    holdout: {
      weighting: "exposure",
      rows: 169_503,
      ae_overall: 0.987,
      ae_by_factor: [
        { factor: "vehicle_age", level: "0-3", actual: 0.063, expected: 0.059, ae: 1.068,
          exposure_years: "5010.75" },
        { factor: "vehicle_age", level: "4-9", actual: 0.046, expected: 0.05, ae: 0.92,
          exposure_years: "8402.0" },
      ],
      lift: [
        { bin: 1, rows: 16_950, predicted: 0.022, actual: 0.025, exposure_years: "1340.5" },
        { bin: 2, rows: 16_950, predicted: 0.05, actual: 0.046, exposure_years: "1333.25" },
      ],
      gini: 0.289,
      gini_normalised: 0.391,
      calibration: [
        { bin: 1, rows: 16_950, predicted: 0.022, actual: 0.025 },
        { bin: 2, rows: 16_950, predicted: 0.05, actual: 0.046 },
      ],
      residual_summary: {
        mean: -0.0011, std: 0.244, minimum: -2.03, maximum: 11.07, p01: -0.63, p99: 0.82,
      },
    },
  },
  complexity: {
    factor_count: 8,
    parameter_count: 214,
    exposure_per_parameter: 1903.4,
    claims_per_parameter: 94.2,
    max_factor_count: null,
    min_exposure_per_parameter: 1000,
  },
  glm: null,
  gbm: {
    eval_curve: [
      { iteration: 0, metric: "poisson-nloglik", train: 0.512, holdout: 0.518 },
      { iteration: 1, metric: "poisson-nloglik", train: 0.487, holdout: 0.499 },
      { iteration: 2, metric: "poisson-nloglik", train: 0.471, holdout: 0.498 },
    ],
    importances: [
      { feature: "vehicle_age", gain: 412.5, cover: 88.1, frequency: 0.34 },
      { feature: "driver_age", gain: 260.2, cover: null, frequency: 0.29 },
    ],
    permutation_importances: [
      { feature: "vehicle_age", baseline: 0.498, permuted: 0.552, degradation: 0.054,
        repeats: 5, seed: 20260824 },
      { feature: "driver_age", baseline: 0.498, permuted: 0.521, degradation: 0.023,
        repeats: 5, seed: 20260824 },
    ],
    partial_dependence: [
      {
        factor: "vehicle_age",
        points: [
          { value: "0-3", mean_prediction: 0.062, exposure_share: 0.31 },
          { value: "4-9", mean_prediction: 0.047, exposure_share: 0.44 },
        ],
        omitted: null,
      },
      {
        factor: "region_x_vehicle_age",
        points: [],
        omitted: { reason: "no_source_column", levels: null, exposure_share: null },
      },
    ],
    monotonicity: [
      { factor: "vehicle_age", declared: "decreasing", holds: true, worst_violation: 0 },
      { factor: "driver_age", declared: "decreasing", holds: false, worst_violation: 0.0031 },
    ],
    tree_count: 300,
    max_depth: 6,
    mean_depth: 4.7,
    quantile_crossing: null,
  },
  // Note, for a reader taking this fixture as a model of a real artifact: it is not one here.
  // `Diagnostics` documents `cross_validation` as populated *iff* the fit's
  // `GlmSpec.select_by == "cv"`, so a GBM — which `gbm` above makes this — was never
  // cross-validated and would carry `null`. No validator enforces that (the artifact does not
  // carry the spec it was fitted from, so it cannot check), which is why this passes. It is
  // one fixture exercising every branch, deliberately, and the combination it depicts is one
  // the platform does not produce.
  cross_validation: {
    method: "random",
    seed: 20260824,
    folds: 5,
    metric: "poisson-nloglik",
    selected_alpha: 0.01,
    path: [
      { alpha: 0, mean_score: 0.505, std_score: 0.004 },
      { alpha: 0.01, mean_score: 0.498, std_score: 0.003 },
      { alpha: 0.1, mean_score: 0.511, std_score: 0.006 },
    ],
    // All five folds, because `folds: 5` says there are five. `CrossValidationDiagnostics`
    // rejects a shorter list — "a fold's dispersion cannot include a fold that was never
    // scored" — so the plan's three-entry version depicted an artifact the backend cannot
    // construct. The scores also reproduce the path point they summarise: their mean is
    // exactly the 0.498 at `selected_alpha`, and their dispersion rounds to that point's
    // 0.003 under both the population and the sample convention, which is what `CvFoldMetric`
    // means by the two reporting "one fact two ways rather than two facts that could drift".
    fold_metrics: [
      { fold: 0, rows: 81_506, score: 0.494 },
      { fold: 1, rows: 81_506, score: 0.502 },
      { fold: 2, rows: 81_506, score: 0.497 },
      { fold: 3, rows: 81_506, score: 0.499 },
      { fold: 4, rows: 81_506, score: 0.498 },
    ],
  },
};
