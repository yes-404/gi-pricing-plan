import { request } from "./client";
import type { components } from "./generated/schema";

export type Profile = components["schemas"]["Profile"];
export type ColumnProfile = components["schemas"]["ColumnProfile"];
export type LevelCount = components["schemas"]["LevelCount"];
export type Histogram = components["schemas"]["Histogram"];
export type OneWaySummary = components["schemas"]["OneWaySummary"];
export type OneWayRow = components["schemas"]["OneWayRow"];
export type ProfileComparison = components["schemas"]["ProfileComparison"];
export type ColumnComparison = components["schemas"]["ColumnComparison"];

/** FR-60. Read, never recomputed — FR-62 forbids the UI computing one. */
export function getProfile(versionId: string): Promise<Profile> {
  return request<Profile>(`/dataset-versions/${versionId}/profile`);
}

/**
 * FR-61, NFR-468: a single lookup into the stored Profile, budgeted at 300 ms.
 *
 * A 404 means the column has no *stored* one-way, which is an answer rather than a
 * failure — the platform refuses to compute one on request, because a fallback that did
 * would meet the budget in testing and miss it in production.
 */
export function getOneWay(versionId: string, column: string): Promise<OneWaySummary> {
  return request<OneWaySummary>(`/dataset-versions/${versionId}/one-ways`, {
    query: { column },
  });
}

/** FR-63. Computed from two stored Profiles, which is why it is cheap enough to GET. */
export function compareProfiles(
  versionId: string,
  against: string,
): Promise<ProfileComparison> {
  return request<ProfileComparison>(`/dataset-versions/${versionId}/compare`, {
    query: { against },
  });
}

/**
 * PSI bands, read from VR-DST-1 rather than restated here.
 *
 * **Two bands, not three.** The removed `"broken"` band asserted a `fail` severity VR-DST-1
 * cannot emit: the rule carries `warn_above` only, and the `fail_above` band is a second
 * catalogue rule that does not exist yet (`FR-56`, built note 2026-08-24). Banding
 * exists so the screen and the rule cannot disagree about one number (`01` §5.3, note of
 * 2026-08-19) — inventing the severe band was that exact disagreement, in the direction that
 * alarms an actuary about a verdict no report will ever carry.
 *
 * When the second rule lands, this gains a third band from *its* `fail_above`. It does not
 * regain a literal.
 *
 * **Takes a `number`, not a nullable one** — `compare_profiles` returns `psi: null` for a
 * column it could not measure, and the caller has to decide. Unchanged.
 */
export function psiBand(psi: number, warnAbove: number): "stable" | "shifted" {
  return psi > warnAbove ? "shifted" : "stable";
}
