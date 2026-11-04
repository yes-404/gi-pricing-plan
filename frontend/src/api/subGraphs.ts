import { request } from "./client";
import type { components } from "./generated/schema";
import type { components as requestComponents } from "./generated/schema.requests";

export type SubGraph = components["schemas"]["SubGraph"];
/** A mount as the save body carries it: the permissive generated set, `inputs`/`outputs` defaulted. */
export type SubGraphRef = requestComponents["schemas"]["SubGraphRef"];

/** One pinned sub-graph version: its ports are what a mount maps (03 FR-217; RL-1835 (i) 5). */
export function getSubGraph(slug: string, version: number): Promise<SubGraph> {
  return request<SubGraph>(`/sub-graphs/${encodeURIComponent(slug)}@${version}`);
}
