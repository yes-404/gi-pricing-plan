import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import type { RelativityDifference } from "@/api/comparisons";
import RelativityDiffTable from "@/components/RelativityDiffTable.vue";

const global = {
  stubs: { RouterLink: { props: ["to"], template: "<a :href='to'><slot /></a>" } },
};

// Tuples rather than arrays, so indexing is defined under `noUncheckedIndexedAccess`.
const REFS = ["model:motor-ad-frequency@7", "model:motor-ad-frequency-gbm@2"] as const;

const DIFFS: [RelativityDifference, RelativityDifference, RelativityDifference] = [
  {
    factor: "driver_age_banded",
    level: "21-25",
    values: [
      { model_ref: REFS[0], value: 1.31 },
      { model_ref: REFS[1], value: 1.34 },
    ],
    max_abs_difference: 0.03,
  },
  {
    factor: "driver_age_banded",
    level: "17-20",
    values: [
      { model_ref: REFS[0], value: 1.718 },
      { model_ref: REFS[1], value: 1.902 },
    ],
    max_abs_difference: 0.184,
  },
  {
    factor: "vehicle_group",
    level: "G12",
    values: [
      { model_ref: REFS[0], value: 0.91 },
      { model_ref: REFS[1], value: null },
    ],
    max_abs_difference: null,
  },
];

describe("RelativityDiffTable", () => {
  it("groups the levels under their factor", () => {
    render(RelativityDiffTable, { props: { differences: DIFFS, modelRefs: REFS }, global });
    expect(screen.getByRole("heading", { name: "driver_age_banded" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "vehicle_group" })).toBeInTheDocument();
  });

  // The largest disagreement is the row a selection decision turns on, and the artifact
  // imposes no order — so this is the view's ordering, applied within a factor only.
  it("orders levels within a factor by descending absolute difference", () => {
    render(RelativityDiffTable, { props: { differences: DIFFS, modelRefs: REFS }, global });
    const table = screen.getByRole("table", { name: /driver_age_banded/ });
    const levels = within(table)
      .getAllByRole("rowheader")
      .map((el) => el.textContent?.trim());
    expect(levels).toEqual(["17-20", "21-25"]);
  });

  // Same rule as the metric table: a null relativity is "does not apply", never zero. Here it
  // also means `max_abs_difference` is null, because a difference against nothing is not 0.
  it("renders a null relativity and a null difference as 'n/a'", () => {
    render(RelativityDiffTable, { props: { differences: [DIFFS[2]], modelRefs: REFS }, global });
    const cells = within(screen.getByRole("row", { name: /G12/ })).getAllByRole("cell");
    expect(cells.map((c) => c.textContent?.trim())).toContain("n/a");
    expect(cells.map((c) => c.textContent?.trim())).not.toContain("0.0000");
  });
});
