// SPIKE F2: correctness of checkConnection and its timing at 200 nodes.
import { appendFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import { buildStructure, checkConnection } from "./graph";

const { nodes, edges } = buildStructure(200);
const conn = (source: string, target: string, targetHandle = "in9") =>
  ({ source, target, sourceHandle: "out", targetHandle });

describe("checkConnection", () => {
  it("builds 200 steps of all seven types", () => {
    expect(nodes).toHaveLength(200);
    expect(new Set(nodes.map((n) => n.type)).size).toBe(7);
  });
  it("s_input_0 has exactly 8 incident edges (the browser run's 328 -> 320 on its delete)", () => {
    expect(edges.filter((e) => e.source === "s_input_0" || e.target === "s_input_0")).toHaveLength(8);
    expect(edges).toHaveLength(328);
  });
  it("rejects each class on deliberately broken input", () => {
    expect(checkConnection(conn("s_table_0", "s_table_0"), nodes, edges)).toBe("self");
    expect(checkConnection(conn("s_output_0", "s_table_1"), nodes, edges)).toBe("no-output");
    expect(checkConnection(conn("s_table_0", "s_input_0"), nodes, edges)).toBe("no-input");
    const e = edges[0]!;
    expect(checkConnection({ ...conn(e.source, e.target), targetHandle: e.targetHandle! }, nodes, edges))
      .toBe("duplicate");
    // A downstream step feeding an upstream one it (transitively) depends on is a cycle.
    const down = edges.find((x) => x.target.startsWith("s_constraint"))!;
    expect(checkConnection(conn(down.target, down.source), nodes, edges)).toBe("cycle");
    // Type mismatch: a relativity into a slot declared for a string.
    const strSlot = nodes.find((n) => n.data!.consumes.some((c) => c.accepts === "string"))!;
    const h = strSlot.data!.consumes.findIndex((c) => c.accepts === "string");
    expect(checkConnection(conn("s_table_69", strSlot.id, `in${h}`), nodes, edges)).not.toBeNull();
    expect(checkConnection(conn("s_input_0", "s_expression_59"), nodes, edges)).toBeNull();
  });
  it("times every ordered pair at 200 nodes, N=5 runs", () => {
    const runs: { p50: number; p99: number; max: number; n: number }[] = [];
    for (let r = 0; r < 5; r++) {
      const t: number[] = [];
      for (const a of nodes) for (const b of nodes) {
        const t0 = performance.now();
        checkConnection(conn(a.id, b.id), nodes, edges);
        t.push(performance.now() - t0);
      }
      t.sort((x, y) => x - y);
      const q = (p: number) => t[Math.min(t.length - 1, Math.floor(p * t.length))]!;
      runs.push({ p50: q(0.5), p99: q(0.99), max: t[t.length - 1]!, n: t.length });
    }
    appendFileSync(process.env.F2_OUT ?? "/dev/null", "F2-TIMING " + JSON.stringify(runs.map((x) => ({
      n: x.n, p50: x.p50.toFixed(4), p99: x.p99.toFixed(4), max: x.max.toFixed(4) }))) + "\n");
    for (const x of runs) expect(x.p99).toBeLessThan(50);
  }, 300_000);
});
