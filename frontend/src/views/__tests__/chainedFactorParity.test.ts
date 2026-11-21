import { describe, expect, it } from "vitest";

import { chainedFactorSlugs, type ChainFactor, type ChainGrouping } from "@/api/diagnostics";

/**
 * FR-109, #1506 slice 5: the view names a model's Factors with a finer level by the fit's rule,
 * re-applied in TypeScript (`chainedFactorSlugs`). The fit's rule is
 * `pricing_core.modelling.diagnostics.chained_factors`. This table is the one both are held to:
 * this file runs the TypeScript rule on it, and `backend/tests/test_api_diagnostics.py` reads
 * the same JSON between the markers and runs the Python rule on it. A change to either rule
 * that the other does not make fails one of the two.
 *
 * `spec_factors` is what the spec pins; `factors` and `groupings` are the dataset's;
 * `loaded` is what the platform's `load_factors` returns for `spec_factors` (pinned, then the
 * interaction operands level by level), which is what the fit hands its rule.
 */
// parity-cases:begin
const CASES = [
  {
    name: "a grouping Factor on a chained grouping",
    spec_factors: ["f-region"],
    factors: [{ id: "f-region", slug: "region", type: "grouping", grouping_id: "g-region" }],
    groupings: [
      { id: "g-region", parent_grouping_id: "g-area" },
      { id: "g-area", parent_grouping_id: null },
    ],
    loaded: ["f-region"],
    expected: ["region"]
  },
  {
    name: "a grouping Factor on an unchained grouping, and an identity Factor",
    spec_factors: ["f-area", "f-age"],
    factors: [
      { id: "f-area", slug: "area", type: "grouping", grouping_id: "g-area" },
      { id: "f-age", slug: "age", type: "identity", grouping_id: null }
    ],
    groupings: [{ id: "g-area", parent_grouping_id: null }],
    loaded: ["f-area", "f-age"],
    expected: []
  },
  {
    name: "an interaction's operand on a chained grouping is named; an unpinned one is not",
    spec_factors: ["f-cross"],
    factors: [
      { id: "f-cross", slug: "cross", type: "interaction", operand_factor_ids: ["f-region", "f-age"] },
      { id: "f-region", slug: "region", type: "grouping", grouping_id: "g-region" },
      { id: "f-age", slug: "age", type: "identity", grouping_id: null },
      { id: "f-other", slug: "other", type: "grouping", grouping_id: "g-region" }
    ],
    groupings: [
      { id: "g-region", parent_grouping_id: "g-area" },
      { id: "g-area", parent_grouping_id: null }
    ],
    loaded: ["f-cross", "f-region", "f-age"],
    expected: ["region"]
  },
  {
    name: "a Factor whose grouping is not among the groupings read",
    spec_factors: ["f-lost"],
    factors: [{ id: "f-lost", slug: "lost", type: "grouping", grouping_id: "g-missing" }],
    groupings: [{ id: "g-area", parent_grouping_id: null }],
    loaded: ["f-lost"],
    expected: []
  }
];
// parity-cases:end

describe("the chained-Factor rule, TypeScript side of the parity table", () => {
  it.each(CASES)("$name", (example) => {
    expect(
      chainedFactorSlugs(
        example.spec_factors,
        example.factors as ChainFactor[],
        example.groupings as ChainGrouping[],
      ),
    ).toEqual(example.expected);
  });
});
