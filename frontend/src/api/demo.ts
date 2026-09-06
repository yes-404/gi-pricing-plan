import { request } from "./client";
import type { components } from "./generated/schema";

export type DemoGuide = components["schemas"]["DemoGuide"];
export type DemoView = components["schemas"]["DemoView"];
export type DemoApiGroup = components["schemas"]["DemoApiGroup"];
export type DemoWorkstream = components["schemas"]["DemoWorkstream"];
export type DemoEndpoint = components["schemas"]["DemoEndpoint"];

/**
 * What is worth driving by hand (FR-409).
 *
 * **404 where the demo entrance is not enabled** — the surface does not exist outside a
 * development identity, which is a different thing from a request that failed, and the
 * entrance view says so rather than showing an error.
 */
export function getGuide(): Promise<DemoGuide> {
  return request<DemoGuide>("/demo/guide");
}

/** Views grouped by the spec that declares them, in spec order. */
export function byModule(guide: DemoGuide): { module: string; views: DemoView[] }[] {
  const groups = new Map<string, DemoView[]>();
  for (const view of guide.views ?? []) {
    const existing = groups.get(view.module);
    if (existing) existing.push(view);
    else groups.set(view.module, [view]);
  }
  return [...groups].map(([module, views]) => ({ module, views }));
}

/** A route with no `:param` can be opened directly; one with params needs a real id. */
export function isOpenable(view: DemoView): boolean {
  return view.implemented && !view.route.includes(":");
}

/** Declared-but-absent endpoints, grouped by the module that declares them. */
export function unpublishedByModule(guide: DemoGuide): { module: string; count: number }[] {
  const counts = new Map<string, number>();
  for (const endpoint of guide.unpublished_endpoints ?? []) {
    counts.set(endpoint.module, (counts.get(endpoint.module) ?? 0) + 1);
  }
  return [...counts].map(([module, count]) => ({ module, count })).sort((a, b) => b.count - a.count);
}
