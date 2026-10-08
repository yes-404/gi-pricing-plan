import type { RatingStep } from "@/api/ratingAlgorithms";

export interface FlowEdge {
  id: string;
  source: string;
  target: string;
  label: string;
}

export function names(value: string | string[] | undefined): string[] {
  if (value === undefined) return [];
  return Array.isArray(value) ? value : [value];
}

/** One edge per consumed name, from its first producer. Draws; never validates (S3 does). */
export function edgesOf(steps: readonly RatingStep[]): FlowEdge[] {
  const producer = new Map<string, string>();
  for (const step of steps) {
    for (const name of names(step.produces)) {
      if (!producer.has(name)) producer.set(name, step.step_id);
    }
  }
  const edges: FlowEdge[] = [];
  for (const step of steps) {
    for (const name of names(step.consumes)) {
      const source = producer.get(name);
      if (source === undefined || source === step.step_id) continue;
      edges.push({
        id: `${source}->${step.step_id}:${name}`,
        source,
        target: step.step_id,
        label: name,
      });
    }
  }
  return edges;
}

/** Kahn's order, ties by declared position; steps left on a cycle are appended in declared order. */
export function graphOrder(steps: readonly RatingStep[]): string[] {
  const ids = steps.map((s) => s.step_id);
  const incoming = new Map(ids.map((id) => [id, 0]));
  const out = new Map<string, string[]>(ids.map((id) => [id, []]));
  for (const e of edgesOf(steps)) {
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
export function layout(steps: readonly RatingStep[]): Record<string, { x: number; y: number }> {
  const depth = new Map<string, number>();
  const edges = edgesOf(steps);
  const order = graphOrder(steps);
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
