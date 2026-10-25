import { request } from "./client";
import type { components } from "./generated/schema";

export type DislocationRun = components["schemas"]["DislocationRun"];
export type DislocationBand = components["schemas"]["DislocationBand"];
export type SegmentSlice = components["schemas"]["SegmentSlice"];
export type RungContribution = components["schemas"]["RungContribution"];
export type AttributionItem = components["schemas"]["AttributionItem"];
export type AttributionSummary = components["schemas"]["AttributionSummary"];
export type DislocationMover = components["schemas"]["DislocationMover"];

/** A persisted Dislocation Run by its id (03 FR-265, `GET /api/v1/dislocation-runs/{id}`). */
export function getDislocationRun(id: string): Promise<DislocationRun> {
  return request<DislocationRun>(`/dislocation-runs/${encodeURIComponent(id)}`);
}

/**
 * The run's movers in §4.6's order, each joined at read to its portfolio columns (FR-263).
 * The row is the generated `DislocationMover`: the stored columns typed, the joined portfolio
 * columns together under `columns` (PL-1833 Task 1).
 */
export function getDislocationMovers(id: string): Promise<DislocationMover[]> {
  return request<DislocationMover[]>(`/dislocation-runs/${encodeURIComponent(id)}/movers`);
}
