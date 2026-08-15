import { request } from "./client";
import type { components } from "./generated/schema";

export type ReferenceTable = components["schemas"]["ReferenceTable"];
export type ReferenceTableVersion = components["schemas"]["ReferenceTableVersion"];
export type ReferenceRow = components["schemas"]["ReferenceRow"];
export type ReferenceLookup = components["schemas"]["ReferenceLookup"];

/** Every declared table. Not paginated — a workspace has tens, not thousands. */
export function listTables(): Promise<ReferenceTable[]> {
  return request<ReferenceTable[]>("/reference-tables");
}

/** The version timeline, newest first, each with the period its rows cover. */
export function listVersions(slug: string): Promise<ReferenceTableVersion[]> {
  return request<ReferenceTableVersion[]>(
    `/reference-tables/${encodeURIComponent(slug)}/versions`,
  );
}

/**
 * Rows of a **pinned** version — the effective-date viewer (`01` §5.3).
 *
 * `asAt` omitted returns the version whole, which answers "what changed?"; a date answers
 * "what applied then?". Neither ever falls back to the latest version: FR-DATA-32 is the
 * rule this screen is most likely to teach by example, and a fallback would teach the
 * opposite of it.
 */
export function listRows(
  slug: string,
  version: number,
  options: { asAt?: string | undefined; limit?: number | undefined } = {},
): Promise<ReferenceRow[]> {
  return request<ReferenceRow[]>(
    `/reference-tables/${encodeURIComponent(slug)}/versions/${version}/rows`,
    { query: { as_at: options.asAt, limit: options.limit } },
  );
}

/** Point lookup, for debugging (FR-DATA-31) — never how rating resolves a reference. */
export function lookup(
  slug: string,
  params: { key: string; asAt: string; version?: number | undefined },
): Promise<ReferenceLookup> {
  return request<ReferenceLookup>(
    `/reference-tables/${encodeURIComponent(slug)}/lookup`,
    { query: { key: params.key, as_at: params.asAt, version: params.version } },
  );
}

/**
 * How a version's coverage reads to a person.
 *
 * A null `covers_to` is **open-ended**, not missing: the version has at least one row that
 * never expires. Rendering it as an empty cell would make the most important case look
 * like absent data.
 */
export function coverage(version: ReferenceTableVersion): string {
  if (!version.covers_from) return "no rows";
  return `${version.covers_from} → ${version.covers_to ?? "open-ended"}`;
}
