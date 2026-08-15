import { request } from "./client";
import type { components } from "./generated/schema";

/**
 * Bandings and groupings — `02` §5.1's six routes, and the two shapes the workbench edits.
 *
 * Every type comes from `./generated/schema`, which is generated from `model-schema` and
 * never hand-written (`CLAUDE.md` §2). A `Banding` in particular has eight fields that
 * decide where a row lands — `closed`, `null_level` and the two range policies among them —
 * and a hand-written copy that fell behind any one of them would show statistics for a
 * banding the platform would not store.
 */

export type Banding = components["schemas"]["Banding"];
export type BandingMethod = components["schemas"]["BandingMethod"];
export type Grouping = components["schemas"]["Grouping"];
export type GroupingMethod = components["schemas"]["GroupingMethod"];
export type GroupingEvidence = components["schemas"]["GroupingEvidence"];
export type OneWayRow = components["schemas"]["OneWayRow"];
export type UnseenLevelBehaviour = components["schemas"]["UnseenLevelBehaviour"];

/** FR-MODEL-9. The platform proposes; nothing is stored until `createBanding`. */
export function proposeBanding(body: {
  dataset_version_id: string;
  column: string;
  method: BandingMethod;
  n_bands: number;
  slug: string;
}): Promise<Banding> {
  return request<Banding>("/bandings/propose", { method: "POST", body });
}

/**
 * FR-MODEL-75. What an edited boundary *did*, before the banding is saved.
 *
 * The whole banding goes over the wire rather than a list of numbers, because the answer
 * depends on all of it — see the module note above.
 */
export function evaluateBanding(
  datasetVersionId: string,
  banding: Banding,
): Promise<Banding> {
  return request<Banding>("/bandings/evaluate", {
    method: "POST",
    body: { dataset_version_id: datasetVersionId, banding },
  });
}

/** FR-MODEL-12. An existing slug allocates the next version rather than editing. */
export function createBanding(banding: Banding): Promise<Banding> {
  return request<Banding>("/bandings", { method: "POST", body: banding });
}

export function listBandings(datasetId?: string): Promise<Banding[]> {
  return request<Banding[]>("/bandings", { query: { dataset_id: datasetId } });
}

/** FR-MODEL-14. */
export function proposeGrouping(body: {
  dataset_version_id: string;
  column: string;
  method: GroupingMethod;
  n_groups: number;
  unseen_level_behaviour: UnseenLevelBehaviour;
  slug: string;
}): Promise<Grouping> {
  return request<Grouping>("/groupings/propose", { method: "POST", body });
}

/** FR-MODEL-75, and the half `02` §5.3 names: the deviance/df trade-off before saving. */
export function evaluateGrouping(
  datasetVersionId: string,
  grouping: Grouping,
): Promise<Grouping> {
  return request<Grouping>("/groupings/evaluate", {
    method: "POST",
    body: { dataset_version_id: datasetVersionId, grouping },
  });
}

/** FR-MODEL-16. Creation is an audited event, because grouping is a modelling decision. */
export function createGrouping(grouping: Grouping): Promise<Grouping> {
  return request<Grouping>("/groupings", { method: "POST", body: grouping });
}

export function listGroupings(datasetId?: string): Promise<Grouping[]> {
  return request<Grouping[]>("/groupings", { query: { dataset_id: datasetId } });
}

/**
 * Replace one boundary, keeping the artifact valid to send back.
 *
 * Boundaries must strictly increase (`02` §4.2), and the platform refuses a set that does
 * not — correctly, but a 422 per keystroke is not an editor. Returning `null` for a move
 * that would cross a neighbour lets the caller mark the input and hold the last good
 * evaluation, which is what "the consequence of an edit" means when the edit is invalid.
 */
export function withBoundary(
  banding: Banding,
  index: number,
  value: number,
): Banding | null {
  if (!Number.isFinite(value)) return null;
  const boundaries = [...banding.boundaries];
  if (index <= 0 || index >= boundaries.length - 1) return null;
  if (value <= boundaries[index - 1]! || value >= boundaries[index + 1]!) return null;
  boundaries[index] = value;
  return { ...banding, boundaries };
}

/**
 * Point one source level at a different target, and drop any target left with no levels.
 *
 * The drop matters: a target level nobody maps to is a level a fitted model would carry a
 * coefficient for and no data behind, which is FR-MODEL-11's objection in the grouping
 * direction.
 */
export function withMapping(
  grouping: Grouping,
  level: string,
  target: string,
): Grouping {
  return { ...grouping, mapping: { ...grouping.mapping, [level]: target } };
}

/** Target levels in first-seen order — `Grouping.target_levels` is a server-side property. */
export function targetLevels(grouping: Grouping): string[] {
  return [...new Set(Object.values(grouping.mapping))];
}

/**
 * How to read a merge's p-value, in the words an actuary would use.
 *
 * The number answers "could these levels be the same?", and the honest reading is the
 * conventional one: above 0.05 the data does not distinguish them, below 0.01 it clearly
 * does. Stated here rather than at the call site so the workbench and any later dossier
 * cannot describe the same number differently.
 */
export function mergeVerdict(
  evidence: GroupingEvidence | null | undefined,
): "supported" | "borderline" | "costly" | "untested" {
  const p = evidence?.chi2_p_value;
  if (p == null) return "untested";
  if (p >= 0.05) return "supported";
  if (p >= 0.01) return "borderline";
  return "costly";
}
