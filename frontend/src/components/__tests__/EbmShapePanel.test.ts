import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import type { EbmFitResult, EbmSpec, EbmTerm } from "@/api/models";

import EbmShapePanel from "../EbmShapePanel.vue";

const SPEC: EbmSpec = {
  model_type: "ebm",
  model_family_slug: "motor-severity",
  dataset_version_id: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
  response_column: "claim_amount",
  objective: "rmse",
  max_bins: 64,
  max_rounds: 50000,
  interactions: 1,
  factors: [],
  offset: { kind: "none" },
  weight: { kind: "none" },
  loss_treatment: { kind: "none" },
  seed: 0,
};

const FIT: EbmFitResult = {
  model_type: "ebm",
  objective: "rmse",
  link: "identity",
  intercept: -2.4181,
  feature_order: ["annual_mileage", "region_grouped"],
  bins: [
    { kind: "numeric", cuts: [5000, 10000, 20000] },
    { kind: "categorical", levels: ["north", "midlands", "south"] },
  ],
  terms: [
    {
      term_name: "annual_mileage",
      term_features: [0],
      scores: [0.0, -0.11, -0.02, 0.07, 0.19, 0.0],
      standard_deviations: [0.0, 0.008, 0.006, 0.005, 0.007, 0.0],
      bin_weights: [0.0, 38214.4, 52110.8, 60452.1, 33489.0, 0.0],
    },
    {
      term_name: "region_grouped",
      term_features: [1],
      scores: [0.0, 0.04, -0.01, 0.02, 0.0],
      standard_deviations: [0.0, 0.003, 0.002, 0.003, 0.0],
      bin_weights: [0.0, 120000.0, 90000.0, 0.0, 0.0],
    },
  ],
  best_iteration: 412,
  rows: 480000,
  fit_seconds: 92.4,
  library_versions: { "interpret-core": "0.7.8" },
};

function cellsOf(table: HTMLElement, column: number): (string | undefined)[] {
  return within(table)
    .getAllByRole("row")
    .slice(1)
    .map((row) => within(row).getAllByRole("cell")[column]?.textContent?.trim());
}

describe("the EBM shape-function panel", () => {
  it("labels a numeric term's bins from its cuts, not by position", () => {
    // `c` cuts give `c + 3` slots: slot 0 unused, `c + 1` populated bins, one trailing missing
    // slot. Reading slot i as "the i-th cut" shifts every score by one bin and still renders a
    // plausible shape function, which is why this has to be asserted rather than eyeballed.
    render(EbmShapePanel, { props: { spec: SPEC, fit: FIT } });
    const table = screen.getByRole("table", { name: "annual_mileage shape function" });
    expect(cellsOf(table, 0)).toEqual([
      "< 5000",
      "5000 – 10000",
      "10000 – 20000",
      "≥ 20000",
      "missing",
    ]);
  });

  it("reads each score from the slot its bin actually occupies", () => {
    // The labels can be right while the scores are off by one, and the result is a shape
    // function that is wrong everywhere and looks wrong nowhere.
    render(EbmShapePanel, { props: { spec: SPEC, fit: FIT } });
    const table = screen.getByRole("table", { name: "annual_mileage shape function" });
    expect(cellsOf(table, 1)).toEqual(["-0.1100", "-0.0200", "0.0700", "0.1900", "0.0000"]);
  });

  it("reads each standard deviation from the same slot as its score", () => {
    // The uncertainty column is what a reader uses to decide whether a bump in the shape
    // function is real, and it was rendered without ever being read back. Both the shift and
    // the total loss were confirmed against this suite before this test existed: replacing
    // `deviations[i + 1]` with `deviations[i]` passed, and so did a hardcoded `sd: 0`.
    render(EbmShapePanel, { props: { spec: SPEC, fit: FIT } });
    const table = screen.getByRole("table", { name: "annual_mileage shape function" });
    expect(cellsOf(table, 2)).toEqual(["0.0080", "0.0060", "0.0050", "0.0070", "0.0000"]);
  });

  it("does not render the unused base slot as a bin", () => {
    // Slot 0 is never reached by a lookup. Rendered as a row it is a bin with a 0.0 score that
    // a reader takes for a real level with no effect.
    render(EbmShapePanel, { props: { spec: SPEC, fit: FIT } });
    const table = screen.getByRole("table", { name: "annual_mileage shape function" });
    expect(within(table).getAllByRole("row")).toHaveLength(6); // 1 header + 5 slots
  });

  it("marks a bin no row landed in, so its zero score is not read as evidence", () => {
    render(EbmShapePanel, { props: { spec: SPEC, fit: FIT } });
    const table = screen.getByRole("table", { name: "region_grouped shape function" });
    const south = within(table).getByText("south").closest("tr")!;
    expect(south).toHaveTextContent(/unpopulated/i);
  });

  it("does not mark a bin that rows did land in", () => {
    // The negative half: a marker on every row says nothing, and would pass the test above.
    render(EbmShapePanel, { props: { spec: SPEC, fit: FIT } });
    const table = screen.getByRole("table", { name: "region_grouped shape function" });
    const north = within(table).getByText("north").closest("tr")!;
    expect(north).not.toHaveTextContent(/unpopulated/i);
  });

  it("renders each bin weight, not merely whether it is zero", () => {
    // The two badge tests above pin the zero/non-zero split, and an off-by-one in the weights
    // does fail them — so alignment is already covered. What they do not pin is the number:
    // replacing every non-zero weight with `1` passed the whole suite. The exposure behind a
    // bin is what a reader weighs its score against, so the figure itself has to be read back.
    //
    // The trailing slot is excluded because its `unpopulated` badge shares the cell, and its
    // text is owned by the two tests above rather than compared as a number here.
    render(EbmShapePanel, { props: { spec: SPEC, fit: FIT } });
    const table = screen.getByRole("table", { name: "annual_mileage shape function" });
    expect(cellsOf(table, 3).slice(0, 4)).toEqual([
      "38,214.4",
      "52,110.8",
      "60,452.1",
      "33,489",
    ]);
  });

  it("names an interaction term and says why it is not tabulated", () => {
    const pair: EbmTerm = {
      term_name: "annual_mileage & region_grouped",
      term_features: [0, 1],
      scores: [
        [0.0, 0.0],
        [0.01, -0.01],
      ],
      standard_deviations: [
        [0.0, 0.0],
        [0.001, 0.001],
      ],
      bin_weights: [
        [0.0, 0.0],
        [100.0, 100.0],
      ],
    };
    render(EbmShapePanel, { props: { spec: SPEC, fit: { ...FIT, terms: [...FIT.terms, pair] } } });
    expect(screen.getByText(/annual_mileage & region_grouped/)).toBeInTheDocument();
    expect(screen.getByText(/two-dimensional/i)).toBeInTheDocument();
  });

  it("says the identity link means a score is an addition, not a multiplier", () => {
    // An EBM's scores are additive on the response scale. Read as relativities they are a
    // different model, and nothing in the numbers themselves says which reading is meant.
    render(EbmShapePanel, { props: { spec: SPEC, fit: FIT } });
    expect(screen.getByText(/identity/i)).toBeInTheDocument();
    expect(screen.getByText(/-2.4181/)).toBeInTheDocument();
  });
});
