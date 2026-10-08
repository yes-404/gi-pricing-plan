import { describe, expect, it } from "vitest";
import type { RatingStep } from "@/api/ratingAlgorithms";
import { edgesOf, graphOrder, layout, parseRef } from "../graph";
import { valid } from "./fixtures";

const steps = valid.steps;

describe("graph derivation", () => {
  it("draws one edge per consumed name, from its producer to its consumer", () => {
    const edges = edgesOf(steps);
    expect(edges).toContainEqual({
      id: "s_in_channel->s_area:channel",
      source: "s_in_channel",
      target: "s_area",
      label: "channel",
    });
    expect(edges).toContainEqual({
      id: "s_area->s_rp:rating_area",
      source: "s_area",
      target: "s_rp",
      label: "rating_area",
    });
    const ids = edges.map((e) => e.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it("draws no edge for a name nothing produces, and none for a step onto itself", () => {
    const dangling = [
      { step_id: "a", type: "expression", consumes: ["ghost"], produces: "x" },
      { step_id: "b", type: "expression", consumes: ["x"], produces: "x" },
      { step_id: "c", type: "expression", consumes: ["y"], produces: "y" },
    ] as unknown as RatingStep[];
    expect(edgesOf(dangling)).toEqual([
      { id: "a->b:x", source: "a", target: "b", label: "x" },
    ]);
  });

  it("orders the topological eleven-step fixture as declared", () => {
    expect(graphOrder(steps)).toEqual([
      "s_in_age",
      "s_in_eff",
      "s_in_channel",
      "s_area",
      "s_rp",
      "s_expense",
      "s_office",
      "s_minprem",
      "s_out_office",
      "s_payable",
      "s_out",
    ]);
  });

  it("terminates on a cycle and appends the steps left on it in declared order", () => {
    const cyclic = [
      { step_id: "a", type: "expression", consumes: ["b"], produces: "a" },
      { step_id: "b", type: "expression", consumes: ["a"], produces: "b" },
    ] as unknown as RatingStep[];
    expect(graphOrder(cyclic)).toEqual(["a", "b"]);
  });

  it("places each step in the column of its longest-path depth, deterministically", () => {
    const at = layout(steps);
    expect(at["s_in_age"]?.x).toBe(0);
    expect(at["s_area"]?.x).toBe(260);
    expect(at["s_rp"]?.x).toBe(520);
    expect(layout(steps)).toEqual(at);
  });

  it("takes depth 0 for a parent not yet placed on a cycle (pinned, so a change is deliberate)", () => {
    const cyclic = [
      { step_id: "a", type: "expression", consumes: ["b"], produces: "a" },
      { step_id: "b", type: "expression", consumes: ["a"], produces: "b" },
    ] as unknown as RatingStep[];
    expect(layout(cyclic)).toEqual({ a: { x: 260, y: 0 }, b: { x: 520, y: 0 } });
  });

  it("parses an artifact reference", () => {
    expect(parseRef("rating_algorithm:motor-gb@14")).toEqual({
      type: "rating_algorithm",
      slug: "motor-gb",
      version: 14,
    });
    expect(() => parseRef("motor-gb")).toThrow();
  });
});
