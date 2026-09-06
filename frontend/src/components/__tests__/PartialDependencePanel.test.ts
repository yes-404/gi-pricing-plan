import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it, vi } from "vitest";

import type { PartialDependence } from "@/api/diagnostics";
import { DIAGNOSTICS } from "@/views/__tests__/fixtures";

import PartialDependencePanel from "../PartialDependencePanel.vue";

vi.mock("vue-echarts", () => ({
  default: {
    name: "VChart",
    props: ["option"],
    template: "<div data-testid='chart'>{{ JSON.stringify(option) }}</div>",
  },
}));

const PD = DIAGNOSTICS.gbm?.partial_dependence ?? [];

const CAPPED: readonly PartialDependence[] = [
  {
    factor: "postcode_sector",
    points: [],
    omitted: { reason: "level_cap", levels: 2841, exposure_share: 0.07 },
  },
];

/**
 * `reason` is a two-member union in the generated type, so an unrecognised value cannot be
 * written without a cast. The cast is the point of the case: the component must survive a
 * reason added to the contract after this build, and the branch is unreachable from a
 * well-typed caller by construction.
 */
const UNKNOWN = [
  {
    factor: "mystery",
    points: [],
    omitted: { reason: "something_new", levels: null, exposure_share: null },
  },
] as unknown as readonly PartialDependence[];

describe("PartialDependencePanel", () => {
  it("draws a figure for a factor that has points", () => {
    render(PartialDependencePanel, { props: { partialDependence: PD } });
    expect(screen.getByRole("table", { name: /vehicle_age/ })).toBeInTheDocument();
  });

  it("carries exposure share, so a curve over almost no exposure is visible as such", () => {
    render(PartialDependencePanel, { props: { partialDependence: PD } });
    const table = screen.getByRole("table", { name: /vehicle_age/ });
    const row = within(table).getByRole("row", { name: /0-3/ });
    expect(within(row).getAllByRole("cell")[2]).toHaveTextContent("0.31");
  });

  it("names an omitted factor rather than leaving it out", () => {
    render(PartialDependencePanel, { props: { partialDependence: PD } });
    expect(screen.getByText(/region_x_vehicle_age/)).toBeInTheDocument();
  });

  it("explains a no_source_column omission in words, not by its enum value", () => {
    render(PartialDependencePanel, { props: { partialDependence: PD } });
    expect(screen.getByText(/sources no column of its own/i)).toBeInTheDocument();
    expect(screen.queryByText("no_source_column")).not.toBeInTheDocument();
  });

  it("explains a level_cap omission and says how many levels were dropped", () => {
    render(PartialDependencePanel, { props: { partialDependence: CAPPED } });
    expect(screen.getByText(/most-exposed levels/i)).toBeInTheDocument();
    expect(screen.getByText(/2841/)).toBeInTheDocument();
  });

  /**
   * Mine, not the plan's. `levels` is documented as "levels present in the data that the sweep
   * did not visit", and the contract's own validator message calls it "the levels it dropped".
   * The plan's sentence rendered it as `2841 levels in total`, which is a different and false
   * claim about the factor — and one a reader would use to judge whether the curve is nearly
   * complete. The count is of what is missing, and the sentence has to say so.
   */
  it("counts the levels the sweep skipped, not the levels the factor has", () => {
    render(PartialDependencePanel, { props: { partialDependence: CAPPED } });
    expect(screen.getByText(/2841 levels were not visited/i)).toBeInTheDocument();
    expect(screen.queryByText(/2841 levels in total/i)).not.toBeInTheDocument();
  });

  /**
   * Also mine. `exposure_share` is what the contract calls "the number that says whether a
   * truncated curve is nearly complete or badly so", and `level_cap` cannot be recorded
   * without it. A truncation reported without it is the unquantified one FR-175 forbids.
   */
  it("says what exposure the omitted levels carry, which decides how bad the truncation is", () => {
    render(PartialDependencePanel, { props: { partialDependence: CAPPED } });
    expect(screen.getByText(/carry 0\.07 of exposure/i)).toBeInTheDocument();
  });

  it("falls back to the raw reason rather than inventing one it does not know", () => {
    render(PartialDependencePanel, { props: { partialDependence: UNKNOWN } });
    expect(screen.getByText(/something_new/)).toBeInTheDocument();
  });
});
