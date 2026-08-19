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

/** FR-DATA-25. Read, never recomputed — FR-DATA-27 forbids the UI computing one. */
export function getProfile(versionId: string): Promise<Profile> {
  return request<Profile>(`/dataset-versions/${versionId}/profile`);
}

/**
 * FR-DATA-26, NFR-DATA-4: a single lookup into the stored Profile, budgeted at 300 ms.
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

/** FR-DATA-28. Computed from two stored Profiles, which is why it is cheap enough to GET. */
export function compareProfiles(
  versionId: string,
  against: string,
): Promise<ProfileComparison> {
  return request<ProfileComparison>(`/dataset-versions/${versionId}/compare`, {
    query: { against },
  });
}

/**
 * PSI bands, as `01` §4.4's VR-DST-1 states them: warn above 0.10, fail above 0.25.
 *
 * The same thresholds the validation rule uses, so a stable-looking column here and a
 * warning in the report cannot disagree about the same number.
 *
 * **Takes a `number`, not a nullable one.** `compare_profiles` returns `psi: null` for a
 * column it could not measure — every column with no non-null `top_levels`. An earlier
 * version answered `"stable"` for that, so an unmeasured column rendered as a calm band
 * rather than as no band at all; the caller now has to decide, and the type makes it.
 */
export function psiBand(psi: number): "stable" | "shifted" | "broken" {
  if (psi > 0.25) return "broken";
  if (psi > 0.1) return "shifted";
  return "stable";
}
