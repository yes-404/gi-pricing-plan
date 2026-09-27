import { request } from "./client";
import { pageThrough, type Paged } from "./paging";
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
 * How many pages `listModels` walks before it stops and says so.
 *
 * **OQ-611**, and the same shape as `OQ-605` one route over: `GET /models`
 * filters by `family`, `status`, `cursor` and `limit` — **not** by dataset version — so a
 * view scoped to a Dataset Version must filter in the client, over a paginated list. A
 * filter applied to one page renders "no models" while matches sit on a later page, and an
 * empty selector is then indistinguishable from a dataset version with no models at all.
 *
 * Its own constant rather than `OBJECTIVE_PAGE_CAP`: the two cite different open questions,
 * and one number in front of two questions is a number nobody can change safely.
 */
export const MODEL_PAGE_CAP = 5;

/**
 * The workspace's models, up to `MODEL_PAGE_CAP` pages, **in the order the route returned
 * them**.
 *
 * Order matters and is not incidental. `Model` carries **no timestamp** — `created_at` is on
 * the row and does not reach the contract — so "most recent" is available only because
 * `list_models` orders by `ModelRow.id.desc()` over UUIDv7 ids, whose leading 48 bits are a
 * millisecond timestamp. Nothing in the type system defends that: a `sort`, a `Map`
 * round-trip or an out-of-order fetch would silently leave callers with an arbitrary model
 * and no error. So this preserves order, and `modelsForVersion` below is tested on order
 * rather than on membership.
 */
export function listModels(): Promise<Paged<Model>> {
  return pageThrough<Model>("/models", {}, MODEL_PAGE_CAP);
}

/**
 * The models fitted on one Dataset Version, newest first, filtered in the client.
 *
 * **`filter` preserves order**, which is the whole of why this is a `filter` and not a
 * lookup: the caller's default is the first element, and that is only "most recent" while
 * the route's ordering survives. Two ids minted in the same millisecond order arbitrarily
 * (`ids.py`), so at that resolution the default is ambiguous — acceptable, because nothing
 * derives ordering within a millisecond, and recorded so it is not later read as a defect.
 *
 * `flags` is **not** read here: `list_models` returns `flags: []` for every row by design.
 */
export function modelsForVersion(page: Paged<Model>, datasetVersionId: string): Model[] {
  return page.items.filter((model) => model.dataset_version_id === datasetVersionId);
}

export type FactorIntent = components["schemas"]["FactorIntent"];
export type MonotonicDirection = components["schemas"]["MonotonicDirection"];

/**
 * Every intent the contract publishes, and what to call it.
 *
 * **A `Record` over the whole union on purpose.** The compiler then enumerates the arms, so
 * a fifth added to `model-schema` is a **build error here** rather than an option that
 * quietly never appears. That is the property a hand-written list of *permitted* intents
 * would not have.
 */
export const FACTOR_INTENT_LABELS: Record<FactorIntent, string> = {
  risk: "Risk — rated on",
  control: "Control — fitted, never rated on",
  offset: "Offset",
  diagnostic: "Diagnostic",
};

/**
 * The intents the platform will not honour, and **the only fact hand-written here**.
 *
 * `offset` is superseded by FR-84 and `diagnostic` by FR-86, both on a layer
 * argument: offsetness and diagnosis are properties of *one fit*, while `Factor.intent`
 * belongs to a Factor defined against a Dataset and reused by every Model Spec naming it.
 * **Both keep their arm in the published contract deliberately**, for artifacts already
 * carrying them — so the union will never narrow to match, and a picker waiting for the
 * type to say which arms are live would wait for ever.
 *
 * Hand-written because no permitted-subset constant exists in the platform. But the
 * *complement* does, machine-readable and shared: `REFUSED_FACTOR_INTENTS` in
 * `pricing-core/modelling/factors.py`. `factorIntents.test.ts` reads that file and fails if
 * the two disagree — which is why the refusal is the thing written down here rather than
 * the permission. A hand-written permitted pair would have no executable authority to pin
 * against, and a newly-live arm would vanish from the picker with nothing failing.
 *
 * **There is no backend fallback.** `POST /factors` accepts all four —
 * `REFUSED_FACTOR_INTENTS` is referenced nowhere under `backend/` — and the only refusal is
 * `resolve_factors`, on the fit path. A superseded intent is accepted, stored and audited,
 * then detonates at fit. So this list is the guard, not a convenience.
 */
export const REFUSED_FACTOR_INTENTS = ["offset", "diagnostic"] as const satisfies
  readonly FactorIntent[];

/** What an actuary may choose: every published arm the platform still honours. */
export const OFFERED_FACTOR_INTENTS = (
  Object.keys(FACTOR_INTENT_LABELS) as FactorIntent[]
).filter((intent) => !(REFUSED_FACTOR_INTENTS as readonly string[]).includes(intent));

/** Same shape, same reason: a `Record` so a new direction is a build error. */
export const MONOTONIC_DIRECTION_LABELS: Record<MonotonicDirection, string> = {
  none: "None",
  increasing: "Increasing",
  decreasing: "Decreasing",
};

/** Create a Factor, or a new version of one (FR-96 — a slug that exists versions). */
export function createFactor(body: {
  slug: string;
  dataset_id: string;
  source_columns: readonly string[];
  intent: FactorIntent;
  monotonic_direction: MonotonicDirection;
  monotonic_rationale?: string | undefined;
}): Promise<Factor> {
  return request<Factor>("/factors", { method: "POST", body });
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
export type ShapSummary = components["schemas"]["ShapSummary"];
export type ShapInteraction = components["schemas"]["ShapInteraction"];

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
 * FR-199 requires a bound to share its central model's Model Family, and the platform
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
 * The model's most recent transparency artifact (FR-139).
 *
 * Addressed by **id**, not slug — `02` §5.1 declares `/models/{id}/transparency` — and it is
 * a 404 for a model that has never had one built. FR-132 makes the artifact an
 * obligation for a non-GLM model only, so a GLM's 404 is not a state worth rendering and
 * this is not called for one.
 */
export function getTransparency(modelId: string): Promise<TransparencyArtifact> {
  return request<TransparencyArtifact>(`/models/${encodeURIComponent(modelId)}/transparency`);
}
