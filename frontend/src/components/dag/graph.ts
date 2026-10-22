import type { RatingStep } from "@/api/ratingAlgorithms";
import type { SubGraphRef } from "@/api/subGraphs";

export interface FlowEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  /** An edge into or out of a purpose mount: it runs only for some quote purposes (RL-1835 (i) 4). */
  conditional: boolean;
}

/** What the drawing needs of a node: a step or a mount (RL-1835 (i) 1 — a mount is a node). */
interface GraphNode {
  id: string;
  consumes: string[];
  produces: string[];
  conditional: boolean;
  mount: boolean;
}

export function isPurposeMount(mount: SubGraphRef): boolean {
  return (mount.purposes ?? []).length > 0;
}

export function names(value: string | string[] | undefined): string[] {
  if (value === undefined) return [];
  return Array.isArray(value) ? value : [value];
}

function nodesOf(steps: readonly RatingStep[], mounts: readonly SubGraphRef[]): GraphNode[] {
  return [
    ...steps.map((s) => ({
      id: s.step_id,
      consumes: names(s.consumes),
      produces: names(s.produces),
      conditional: false,
      mount: false,
    })),
    ...mounts.map((m) => ({
      id: m.mount_point,
      consumes: Object.values(m.inputs ?? {}),
      produces: Object.values(m.outputs ?? {}),
      conditional: isPurposeMount(m),
      mount: true,
    })),
  ];
}

/**
 * One edge per consumed name, from its first producer; a mount also draws an edge to each consumer
 * of a name it re-produces (RL-1628), so its detour is visible. Draws; never validates (S3 does).
 */
export function edgesOf(steps: readonly RatingStep[], mounts: readonly SubGraphRef[] = []): FlowEdge[] {
  const nodes = nodesOf(steps, mounts);
  const byId = new Map(nodes.map((n) => [n.id, n]));
  const producers = new Map<string, string[]>();
  for (const node of nodes) {
    for (const name of node.produces) {
      const list = producers.get(name) ?? [];
      if (list.length === 0 || (node.mount && !list.includes(node.id))) list.push(node.id);
      producers.set(name, list);
    }
  }
  const edges: FlowEdge[] = [];
  for (const node of nodes) {
    for (const name of node.consumes) {
      for (const source of producers.get(name) ?? []) {
        if (source === node.id) continue;
        edges.push({
          id: `${source}->${node.id}:${name}`,
          source,
          target: node.id,
          label: name,
          conditional: node.conditional || (byId.get(source)?.conditional ?? false),
        });
      }
    }
  }
  return edges;
}

/** Kahn's order, ties by declared position; steps left on a cycle are appended in declared order. */
export function graphOrder(steps: readonly RatingStep[], mounts: readonly SubGraphRef[] = []): string[] {
  const ids = [...steps.map((s) => s.step_id), ...mounts.map((m) => m.mount_point)];
  const incoming = new Map(ids.map((id) => [id, 0]));
  const out = new Map<string, string[]>(ids.map((id) => [id, []]));
  for (const e of edgesOf(steps, mounts)) {
    incoming.set(e.target, (incoming.get(e.target) ?? 0) + 1);
    out.get(e.source)?.push(e.target);
  }
  const order: string[] = [];
  const ready = ids.filter((id) => incoming.get(id) === 0);
  while (ready.length > 0) {
    const id = ready.shift() as string;
    order.push(id);
    for (const next of out.get(id) ?? []) {
      const left = (incoming.get(next) ?? 0) - 1;
      incoming.set(next, left);
      if (left === 0) ready.splice(insertionIndex(ready, next, ids), 0, next);
    }
  }
  return order.concat(ids.filter((id) => !order.includes(id)));
}

function insertionIndex(ready: string[], id: string, ids: string[]): number {
  const at = ids.indexOf(id);
  const index = ready.findIndex((r) => ids.indexOf(r) > at);
  return index === -1 ? ready.length : index;
}

const COLUMN = 260;
const ROW = 120;

/** Column = longest-path depth; row = order within the column. Deterministic. */
export function layout(
  steps: readonly RatingStep[],
  mounts: readonly SubGraphRef[] = [],
): Record<string, { x: number; y: number }> {
  const depth = new Map<string, number>();
  const edges = edgesOf(steps, mounts);
  const order = graphOrder(steps, mounts);
  for (const id of order) {
    const parents = edges.filter((e) => e.target === id).map((e) => depth.get(e.source) ?? 0);
    depth.set(id, parents.length === 0 ? 0 : Math.max(...parents) + 1);
  }
  const rows = new Map<number, number>();
  const at: Record<string, { x: number; y: number }> = {};
  for (const id of order) {
    const column = depth.get(id) ?? 0;
    const row = rows.get(column) ?? 0;
    rows.set(column, row + 1);
    at[id] = { x: column * COLUMN, y: row * ROW };
  }
  return at;
}

export function parseRef(ref: string): { type: string; slug: string; version: number } {
  const match = /^([a-z_]+):([^@]+)@(\d+)$/.exec(ref);
  if (match === null) throw new Error(`not an artifact reference: ${ref}`);
  return { type: match[1] as string, slug: match[2] as string, version: Number(match[3]) };
}
