// RL-1835 (i) items 1, 3, 4: a mount is a node of the graph, drawn by the producer -> consumer rule.
import { describe, expect, it } from "vitest";

import { edgesOf, graphOrder, layout } from "../graph";
import { valid } from "./fixtures";
import { FEES, REFUND } from "./mountFixtures";

const steps = valid.steps;

describe("a mount counted as a node (RL-1835 (i) 3)", () => {
  it("draws an edge from the producer of each mapped input to the mount", () => {
    const edge = edgesOf(steps, [FEES]).find((e) => e.target === "m_fees");
    expect(edge).toMatchObject({ source: "s_office", label: "office_premium_minor" });
  });

  it("draws an edge from the mount to each consumer of a name only it produces", () => {
    const consumer = {
      step_id: "s_use",
      type: "expression",
      label: "x",
      expr: "fees_total",
      result_type: "decimal",
      consumes: ["fees_total"],
      produces: "used",
    } as unknown as (typeof steps)[number];
    const edge = edgesOf([...steps, consumer], [FEES]).find((e) => e.target === "s_use");
    expect(edge).toMatchObject({ source: "m_fees", label: "fees_total" });
  });

  it("also draws the mount's edge to a consumer of a parent name it re-produces, dashed", () => {
    const into = edgesOf(steps, [REFUND]).filter((e) => e.target === "m_refund");
    expect(into.map((e) => e.conditional)).toEqual([true]);
    const out = edgesOf(steps, [REFUND]).filter((e) => e.source === "m_refund");
    expect(out.length).toBeGreaterThan(0);
    expect(out.every((e) => e.conditional)).toBe(true);
    expect(out.map((e) => e.target)).toContain("s_out");
  });

  it("marks no edge conditional for an unconditional mount or a step", () => {
    expect(edgesOf(steps, [FEES]).some((e) => e.conditional)).toBe(false);
  });

  it("puts the mount in the order and the layout", () => {
    expect(graphOrder(steps, [FEES])).toContain("m_fees");
    expect(layout(steps, [FEES])["m_fees"]).toBeDefined();
  });
});
