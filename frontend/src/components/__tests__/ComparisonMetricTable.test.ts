import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import type { ComparisonMetric } from "@/api/comparisons";
import ComparisonMetricTable from "@/components/ComparisonMetricTable.vue";

const global = {
  stubs: { RouterLink: { props: ["to"], template: "<a :href='to'><slot /></a>" } },
};
// Both fixtures are tuples rather than arrays, so that indexing them is defined under
// `noUncheckedIndexedAccess` — otherwise every `REFS[0]` below is `string | undefined` and
// needs a `!` that would also hide a genuinely missing element.
const REFS = ["model:motor-ad-frequency@7", "model:motor-ad-frequency-gbm@2"] as const;

const METRICS: [ComparisonMetric, ComparisonMetric, ComparisonMetric] = [
  {
    metric: "gini_normalised",
    weighting: "exposure",
    direction: "higher_is_better",
    values: [
      { model_ref: REFS[0], value: 0.412 },
      { model_ref: REFS[1], value: 0.43 },
    ],
    leader: REFS[1],
  },
  {
    metric: "rows",
    weighting: "exposure",
    direction: "not_ordered",
    values: [
      { model_ref: REFS[0], value: 169503 },
      { model_ref: REFS[1], value: 169503 },
    ],
    leader: null,
  },
  {
    metric: "deviance_ratio",
    weighting: "exposure",
    direction: "lower_is_better",
    values: [
      { model_ref: REFS[0], value: 0.77 },
      { model_ref: REFS[1], value: null },
    ],
    leader: REFS[0],
  },
];

function row(name: string): HTMLElement {
  return screen.getByRole("row", { name: new RegExp(name) });
}

describe("ComparisonMetricTable", () => {
  it("puts every model in a column and every metric in a row", () => {
    render(ComparisonMetricTable, { props: { metrics: METRICS, modelRefs: REFS }, global });
    expect(screen.getAllByRole("columnheader")).toHaveLength(REFS.length + 2); // metric, direction, two models
    expect(screen.getAllByRole("row")).toHaveLength(METRICS.length + 1);
  });

  // `02` §4.11: leader is null "where the metric does not order **or the models tie**". Two
  // different measurements, so they get two different words — not one blank cell each.
  it("says 'not ranked' for an unordered metric and 'tied' for a tie", () => {
    const tied: ComparisonMetric = { ...METRICS[0], leader: null };
    render(ComparisonMetricTable, {
      props: { metrics: [METRICS[1], tied], modelRefs: REFS },
      global,
    });
    expect(within(row("rows")).getByText(/not ranked/i)).toBeInTheDocument();
    expect(within(row("gini_normalised")).getByText(/tied/i)).toBeInTheDocument();
  });

  // §4.11: a value is null "where the metric does not apply, because a missing model reads as
  // one that scored nothing rather than one nobody measured". Rendering 0 or an empty cell is
  // the exact misreading that sentence forbids.
  it("renders a null value as 'n/a', never as a number", () => {
    render(ComparisonMetricTable, { props: { metrics: [METRICS[2]], modelRefs: REFS }, global });
    // The metric name is a `<th scope="row">`, whose role is `rowheader` and not `cell`, so
    // the model columns start at index 1: [direction, model 0, model 1].
    const cells = within(row("deviance_ratio")).getAllByRole("cell");
    expect(cells[1]).toHaveTextContent("0.77");
    expect(cells[2]).toHaveTextContent("n/a");
    expect(cells[2]).not.toHaveTextContent("0");
  });

  // The direction is on the row because §4.11 makes it "part of the metric, not the reader's
  // assumption" — a reader who cannot see it cannot tell whether 1.4 beat 1.0.
  it("shows each metric's direction", () => {
    render(ComparisonMetricTable, { props: { metrics: METRICS, modelRefs: REFS }, global });
    expect(within(row("gini_normalised")).getByText(/higher is better/i)).toBeInTheDocument();
    expect(within(row("deviance_ratio")).getByText(/lower is better/i)).toBeInTheDocument();
  });
});
