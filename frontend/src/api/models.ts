import { request } from "./client";
import type { components } from "./generated/schema";

export type Model = components["schemas"]["Model"];
export type GlmFitResult = components["schemas"]["GlmFitResult"];
export type Coefficient = components["schemas"]["Coefficient"];
export type RelativityLevel = components["schemas"]["RelativityLevel"];
export type Factor = components["schemas"]["Factor"];

/** The model artifact — latest version, or the one named. */
export function getModel(slug: string, version?: number): Promise<Model> {
  return request<Model>(`/models/${encodeURIComponent(slug)}`, {
    query: { version },
  });
}

/** Factors defined against a dataset, newest version of each first. */
export function listFactors(datasetId?: string): Promise<Factor[]> {
  return request<Factor[]>("/factors", { query: { dataset_id: datasetId } });
}

/**
 * How wide an interval is, in the units of the coefficient — `high - low` on the 95%
 * interval, not a fraction of the estimate.
 *
 * `02` R5 makes uncertainty part of what an estimate *is*, and a table of point estimates
 * invites exactly the reading it exists to prevent: that a relativity of 1.72 on 40 rows
 * and one on 400 000 mean the same thing. R5 requires that the uncertainty be carried and
 * does not name a width statistic, so the absolute width is a choice this helper makes
 * rather than one the spec dictates; a caller wanting a scale-free measure divides by
 * `estimate` itself.
 */
export function intervalWidth(coefficient: Coefficient): number {
  const [low, high] = coefficient.ci_95;
  return high - low;
}

/** A coefficient whose interval spans zero has not been distinguished from no effect. */
export function spansZero(coefficient: Coefficient): boolean {
  const [low, high] = coefficient.ci_95;
  return low <= 0 && high >= 0;
}

/** Relativity intervals, exponentiated for a log link — what the table actually shows. */
export function relativityInterval(coefficient: Coefficient): [number, number] {
  const [low, high] = coefficient.ci_95;
  return [Math.exp(low), Math.exp(high)];
}

export type GlmSpec = components["schemas"]["GlmSpec"];
export type GbmSpec = components["schemas"]["GbmSpec"];
export type EbmSpec = components["schemas"]["EbmSpec"];
export type GbmFitResult = components["schemas"]["GbmFitResult"];
export type EbmFitResult = components["schemas"]["EbmFitResult"];
export type EbmTerm = components["schemas"]["EbmTerm"];
export type TransparencyArtifact = components["schemas"]["TransparencyArtifact"];

/**
 * The GBM arm is two `model_type` values, not one.
 *
 * `02` §4.4, amended 2026-08-17: `GbmSpec.backend` was removed because two fields held one
 * fact, and `model_type` — the discriminator the union already turns on — is what survived.
 * So xgboost and lightgbm are one arm with the backend written into the tag, and a narrower
 * that forgets the second renders an empty page for half the boosters this platform fits.
 */
export function gbmSpec(model: Model): GbmSpec | null {
  const spec = model.spec;
  return spec.model_type === "xgboost" || spec.model_type === "lightgbm" ? spec : null;
}

export function ebmSpec(model: Model): EbmSpec | null {
  const spec = model.spec;
  return spec.model_type === "ebm" ? spec : null;
}

export function gbmFit(model: Model): GbmFitResult | null {
  const fit = model.fit_result ?? null;
  return fit?.model_type === "xgboost" || fit?.model_type === "lightgbm" ? fit : null;
}

export function ebmFit(model: Model): EbmFitResult | null {
  const fit = model.fit_result ?? null;
  return fit?.model_type === "ebm" ? fit : null;
}

/**
 * Where the model a bound bounds lives, or `null` if this model is not a bound.
 *
 * FR-MODEL-78 requires a bound to share its central model's Model Family, and the platform
 * refuses a mismatch before a Job exists (`MODEL_INTERVAL_PAIR_INVALID`, compared on family
 * slug, dataset version, split ref and the factor set). The slug on this model is therefore
 * the central model's slug, and `interval_for.model_version` is its version — both read off
 * the contract. `interval_for.model_id` is a bare UUID and no read resolves one to a route,
 * which is why this returns the slug rather than it.
 */
export function boundCentral(
  model: Model,
): { slug: string; version: number; alpha: number } | null {
  const bound = gbmSpec(model)?.interval_for ?? null;
  if (bound === null) return null;
  return { slug: model.model_family_slug, version: bound.model_version, alpha: bound.alpha };
}

/**
 * The model's most recent transparency artifact (FR-MODEL-84).
 *
 * Addressed by **id**, not slug — `02` §5.1 declares `/models/{id}/transparency` — and it is
 * a 404 for a model that has never had one built. FR-MODEL-33 makes the artifact an
 * obligation for a non-GLM model only, so a GLM's 404 is not a state worth rendering and
 * this is not called for one.
 */
export function getTransparency(modelId: string): Promise<TransparencyArtifact> {
  return request<TransparencyArtifact>(`/models/${encodeURIComponent(modelId)}/transparency`);
}
