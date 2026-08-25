import { pageThrough, type Paged } from "./paging";
import { request } from "./client";
import type { components } from "./generated/schema";

export type PerilStructure = components["schemas"]["PerilStructure"];
export type PerilStructureStatus = components["schemas"]["PerilStructureStatus"];

/**
 * How many pages `listPerilStructures` will fetch before it stops and says so.
 *
 * Matches `OBJECTIVE_PAGE_CAP` deliberately: the two libraries are the same screen over
 * different artifacts, and a reader who learns one cap should not find a second number here.
 * `truncated` is part of the return type rather than a log line for the reason `objectives.ts`
 * gives — an empty page under a truncated sweep is indistinguishable from an empty library.
 */
export const PERIL_STRUCTURE_PAGE_CAP = 5;

export async function listPerilStructures(
  options: { status?: PerilStructureStatus | undefined; slug?: string | undefined } = {},
): Promise<Paged<PerilStructure>> {
  return pageThrough<PerilStructure>(
    "/peril-structures",
    { status: options.status, slug: options.slug },
    PERIL_STRUCTURE_PAGE_CAP,
  );
}

export async function getPerilStructure(id: string): Promise<PerilStructure> {
  return request<PerilStructure>(`/peril-structures/${encodeURIComponent(id)}`);
}
