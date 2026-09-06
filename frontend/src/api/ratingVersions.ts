import { request } from "./client";
import type { components } from "./generated/schema";

export type RatingVersion = components["schemas"]["RatingVersion"];

/** The Phase 1b rating versions the demo seeds (FR-440, W7-5). */
export function listRatingVersions(): Promise<RatingVersion[]> {
  return request<RatingVersion[]>("/rating-versions");
}

export function getRatingVersion(id: string): Promise<RatingVersion> {
  return request<RatingVersion>(`/rating-versions/${encodeURIComponent(id)}`);
}
