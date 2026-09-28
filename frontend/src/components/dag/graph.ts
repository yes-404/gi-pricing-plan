// SPIKE F2 (2026-09-28), scratch only. `RatingStepSpike` MIRRORS a subset of
// `docs/contracts/schemas/rating-algorithm.schema.json` `steps[]` by hand ONLY because
// `RatingAlgorithm` (model-schema `rating.py`) is not yet exposed in the generated OpenAPI
// (`docs/contracts/openapi/generated.json` has no RatingAlgorithm component). WK-675 must
// generate it (CLAUDE.md §2) before building this for real.
import type { Connection, Edge, Node } from "@vue-flow/core";

export const STEP_TYPES = [
  "input", "lookup", "table", "expression", "model_call", "constraint", "output",
] as const;
export type StepType = (typeof STEP_TYPES)[number];
export type ResultType = "int" | "decimal" | "money_minor" | "relativity" | "percentage" | "string" | "bool";

export interface RatingStepSpike {
  step_id: string;
  type: StepType;
  label: string;
  produces: string | null; // one derived value per step in this spike
  result_type: ResultType;
  consumes: { name: string; accepts: ResultType }[];
}

export type StepNode = Node<RatingStepSpike>;

/** Deterministic ~200-step motor-like structure (03 NFR-489's "~200-step motor structure"). */
export function buildStructure(n = 200): { nodes: StepNode[]; edges: Edge[] } {
  // Layer plan: inputs, lookups, tables, model_calls, expressions, constraints, outputs.
  const plan: [StepType, number, ResultType][] = [
    ["input", 30, "string"], ["lookup", 10, "string"], ["table", 70, "relativity"],
    ["model_call", 5, "decimal"], ["expression", 60, "decimal"], ["constraint", 20, "decimal"],
    ["output", n - 195, "money_minor"],
  ];
  const nodes: StepNode[] = [];
  const edges: Edge[] = [];
  let seed = 42;
  const rnd = () => ((seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648);
  const byLayer: StepNode[][] = [];
  plan.forEach(([type, count, rt], layer) => {
    const layerNodes: StepNode[] = [];
    for (let i = 0; i < count; i++) {
      const id = `s_${type}_${i}`;
      const upstream = byLayer.flat();
      const k = type === "input" ? 0 : type === "output" ? 1 : 1 + Math.floor(rnd() * 3);
      const picks: StepNode[] = [];
      for (let j = 0; j < k && upstream.length; j++) {
        const u = upstream[Math.floor(rnd() * upstream.length)]!;
        if (!picks.includes(u)) picks.push(u);
      }
      const data: RatingStepSpike = {
        step_id: id, type, label: `${type} ${i}`,
        produces: type === "output" ? null : `v_${id}`,
        result_type: rt,
        consumes: picks.map((u) => ({ name: u.data!.produces!, accepts: u.data!.result_type })),
      };
      const node: StepNode = {
        id, type, data,
        position: { x: layer * 260, y: i * 70 },
      };
      picks.forEach((u, h) => edges.push({
        id: `e_${u.id}_${id}_${h}`, source: u.id, target: id,
        sourceHandle: "out", targetHandle: `in${h}`,
      }));
      layerNodes.push(node);
      nodes.push(node);
    }
    byLayer.push(layerNodes);
  });
  return { nodes, edges };
}

export type Rejection = "self" | "no-output" | "no-input" | "type-mismatch" | "duplicate" | "cycle";

/**
 * Live validation for Vue Flow's `isValidConnection`: FR-212 (acyclic) and FR-240 (types
 * compatible). Deliberately rebuilds adjacency on every call (no cache): the worst case.
 */
export function checkConnection(
  c: Pick<Connection, "source" | "target" | "sourceHandle" | "targetHandle">,
  nodes: readonly StepNode[], edges: readonly Edge[],
): Rejection | null {
  if (c.source === c.target) return "self";
  const byId = new Map(nodes.map((n) => [n.id, n]));
  const src = byId.get(c.source)?.data;
  const tgt = byId.get(c.target)?.data;
  if (!src || src.produces === null) return "no-output";
  if (!tgt || tgt.type === "input") return "no-input";
  const slot = tgt.consumes[Number((c.targetHandle ?? "in0").slice(2))];
  if (slot && slot.accepts !== src.result_type) return "type-mismatch";
  if (edges.some((e) => e.source === c.source && e.target === c.target)) return "duplicate";
  // Cycle iff target already reaches source.
  const out = new Map<string, string[]>();
  for (const e of edges) (out.get(e.source) ?? out.set(e.source, []).get(e.source)!).push(e.target);
  const stack = [c.target];
  const seen = new Set<string>();
  while (stack.length) {
    const v = stack.pop()!;
    if (v === c.source) return "cycle";
    if (seen.has(v)) continue;
    seen.add(v);
    for (const w of out.get(v) ?? []) stack.push(w);
  }
  return null;
}
