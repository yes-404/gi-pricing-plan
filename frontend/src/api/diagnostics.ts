import { request } from "./client";
import type { components } from "./generated/schema";

export type Diagnostics = components["schemas"]["Diagnostics"];
export type UniversalDiagnostics = components["schemas"]["UniversalDiagnostics"];
export type PartitionDiagnostics = components["schemas"]["PartitionDiagnostics"];
export type AeCell = components["schemas"]["AeCell"];
export type LiftBin = components["schemas"]["LiftBin"];
export type CalibrationBin = components["schemas"]["CalibrationBin"];
export type ResidualSummary = components["schemas"]["ResidualSummary"];
export type ComplexityDiagnostic = components["schemas"]["ComplexityDiagnostic"];
export type GlmDiagnostics = components["schemas"]["GlmDiagnostics"];
export type TypeIIITest = components["schemas"]["TypeIIITest"];
export type GbmDiagnostics = components["schemas"]["GbmDiagnostics"];
export type GbmEvalPoint = components["schemas"]["GbmEvalPoint"];
export type FeatureImportance = components["schemas"]["FeatureImportance"];
export type PermutationImportance = components["schemas"]["PermutationImportance"];
export type PartialDependence = components["schemas"]["PartialDependence"];
export type PartialDependencePoint = components["schemas"]["PartialDependencePoint"];
export type PartialDependenceOmission = components["schemas"]["PartialDependenceOmission"];
export type MonotonicityCheck = components["schemas"]["MonotonicityCheck"];
export type QuantileCrossing = components["schemas"]["QuantileCrossing"];
export type CrossValidationDiagnostics = components["schemas"]["CrossValidationDiagnostics"];
export type CvPathPoint = components["schemas"]["CvPathPoint"];
export type CvFoldMetric = components["schemas"]["CvFoldMetric"];

/**
 * The evidence behind a fitted model (FR-170, `02` §5.1).
 *
 * Read, never recomputed — the endpoint returns what the fit recorded, and a screen that
 * recalculated a diagnostic would be showing a number no approval could cite. `?version=`
 * selects a model version exactly as `getModel` does; the latest without it.
 */
export function getDiagnostics(slug: string, version?: number): Promise<Diagnostics> {
  return request<Diagnostics>(`/models/${encodeURIComponent(slug)}/diagnostics`, {
    query: { version },
  });
}

export type PartitionLabel = "Train" | "Holdout";

/**
 * What a shared instrument may caption a column.
 *
 * `PartitionLabel` is the *fit's* two partitions and keeps that exact meaning — a backtest's
 * single partition is neither of them (FR-187), and the instruments interpolate whatever
 * they are given straight into a heading. Widening `PartitionLabel` itself would make
 * `partitions()` advertise a member it can never produce.
 *
 * Closed rather than `string`: FR-187 forbids a caption that "asserts a relationship the
 * artifact does not carry", so a new member is a spec question, not a type change.
 */
export type PartitionCaption = PartitionLabel | "Backtest";

/**
 * The two partitions, in the order they are read.
 *
 * FR-183: `UniversalDiagnostics` requires `train` and `holdout` as separate
 * `PartitionDiagnostics`, so a one-sided universal diagnostic is unrepresentable and this
 * helper cannot return fewer than two. It exists so that every universal instrument iterates
 * the same pair in the same order rather than each writing `[['Train', u.train], …]` again —
 * a chart that plotted holdout first would compare against the neighbouring chart wrongly.
 *
 * There is no matching helper for `glm`, `complexity` or `cross_validation`: those declare
 * neither field, and a helper suggesting otherwise is the misreading this slice guards.
 */
export function partitions(
  universal: UniversalDiagnostics,
): readonly (readonly [PartitionLabel, PartitionDiagnostics])[] {
  return [
    ["Train", universal.train],
    ["Holdout", universal.holdout],
  ] as const;
}

/**
 * FR-184: an unweighted metric on an exposure-weighted problem is labelled as such,
 * which the UI can only do if the fit said which. The words matter — "count" is the enum
 * value and "unweighted (row count)" is what an actuary needs to read next to a Gini.
 *
 * An unrecognised value returns unchanged rather than mapping to a default: a new weighting
 * shown under the wrong English is worse than one shown under its own identifier.
 */
export function weightingLabel(weighting: string): string {
  const words: Record<string, string> = {
    exposure: "exposure-weighted",
    claim_count: "claim-count-weighted",
    count: "unweighted (row count)",
  };
  return words[weighting] ?? weighting;
}
