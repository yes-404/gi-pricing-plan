import { pageThrough, type Paged } from "./paging";
import type { components } from "./generated/schema";

export type Environment = components["schemas"]["Environment"];

/**
 * How many pages `listEnvironments` will fetch before it stops and says so.
 *
 * **FR-1903.** The Rating version list's live badges are a join over every Environment's
 * `live_deployments`, so a first page alone is not the source: a version live only in an
 * environment on page two would read as live nowhere. A caller that meets `truncated` treats
 * the live set as unknown, never as short. 5 pages of `PAGE_SIZE` is far beyond the number of
 * environments a workspace declares (`07` §4.2); the cap exists so the walk ends, not because
 * it is expected to be reached.
 */
export const ENVIRONMENT_PAGE_CAP = 5;

/** `GET /environments`, every page — needs `settings:read`, which a custom role may lack. */
export function listEnvironments(): Promise<Paged<Environment>> {
  return pageThrough<Environment>("/environments", {}, ENVIRONMENT_PAGE_CAP);
}

/** The `ArtifactRef` string a `LiveDeployment` names a Rating Version by (FR-1531's pair). */
export function ratingVersionRef(slug: string, version: number): string {
  return `rating_version:${slug}@${version}`;
}
