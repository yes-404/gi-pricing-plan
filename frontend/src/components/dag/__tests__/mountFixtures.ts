// A draft with two mounts for the SL-1554 tests (RL-1835): one unconditional, one cancellation-only
// that re-produces a parent name (RL-1628). Shapes come from the generated client, never hand-written.
import type { RatingAlgorithmDraft } from "@/api/ratingAlgorithms";
import type { SubGraph, SubGraphRef } from "@/api/subGraphs";

import { valid } from "./fixtures";

export const FEES: SubGraphRef = {
  ref: "sub_graph:ipt-and-fees@1",
  mount_point: "m_fees",
  inputs: { base: "office_premium_minor" },
  outputs: { total: "fees_total" },
};

export const REFUND: SubGraphRef = {
  ref: "sub_graph:short-period-refund@2",
  mount_point: "m_refund",
  inputs: { premium: "payable_value" },
  outputs: { refund: "payable_value" },
  purposes: ["cancellation"],
};

export const withMounts: RatingAlgorithmDraft = { ...valid, sub_graphs: [FEES, REFUND] };

export const PINS = [FEES.ref, REFUND.ref];

export const FRAGMENT: SubGraph = {
  slug: "ipt-and-fees",
  version: 1,
  change_note: "first",
  inputs: [
    { name: "base", type: "money_minor" },
    { name: "rate", type: "decimal" },
  ],
  outputs: [
    { name: "total", type: "money_minor", required: true },
    { name: "ipt", type: "money_minor", required: false },
  ],
  steps: [],
};
