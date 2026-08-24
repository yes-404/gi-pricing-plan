import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it, vi } from "vitest";

import { DIAGNOSTICS } from "@/views/__tests__/fixtures";

import CrossValidationPanel from "../CrossValidationPanel.vue";

vi.mock("vue-echarts", () => ({
  default: {
    name: "VChart",
    props: ["option"],
    template: "<div data-testid='chart'>{{ JSON.stringify(option) }}</div>",
  },
}));

/** The path chart is mounted first, the fold chart second. */
function pathOption(): {
  yAxis: { name: string };
  series: { name: string; data: number[] }[];
} {
  return JSON.parse(screen.getAllByTestId("chart")[0]?.textContent ?? "{}");
}

const CV = DIAGNOSTICS.cross_validation!;

describe("CrossValidationPanel", () => {
  it("names the fold construction and the seed that reproduces it", () => {
    render(CrossValidationPanel, { props: { crossValidation: CV } });
    const table = screen.getByRole("table", { name: /cross-validation/i });
    expect(within(table).getByRole("row", { name: /method/i })).toHaveTextContent("random");
    expect(within(table).getByRole("row", { name: /seed/i })).toHaveTextContent("20260824");
  });

  it("marks which alpha was selected, not just the path it was selected from", () => {
    render(CrossValidationPanel, { props: { crossValidation: CV } });
    const table = screen.getByRole("table", { name: /regularisation path/i });
    const row = within(table).getByRole("row", { name: /^0\.01/ });
    expect(row).toHaveTextContent(/selected/i);
  });

  /**
   * Mine, not the plan's. The plan asserts the selected alpha's row says "Selected" and stops
   * there — a panel that marked *every* row would pass it. The marker's whole content is that
   * it distinguishes one alpha from the others, so the count is the assertion.
   */
  it("marks exactly one alpha, which is the only thing the marker can mean", () => {
    render(CrossValidationPanel, { props: { crossValidation: CV } });
    const table = screen.getByRole("table", { name: /regularisation path/i });
    const marked = within(table)
      .getAllByRole("row")
      .filter((row) => /selected/i.test(row.textContent ?? ""));
    expect(marked).toHaveLength(1);
  });

  it("plots one point per fold rather than their mean, which is the dispersion", () => {
    render(CrossValidationPanel, { props: { crossValidation: CV } });
    const table = screen.getByRole("table", { name: /fold dispersion/i });
    expect(within(table).getAllByRole("row")).toHaveLength(CV.fold_metrics.length + 1);
  });

  it("carries the std score into the path table, since a mean without it is not a choice", () => {
    render(CrossValidationPanel, { props: { crossValidation: CV } });
    const table = screen.getByRole("table", { name: /regularisation path/i });
    const row = within(table).getByRole("row", { name: /^0\.01/ });
    expect(within(row).getAllByRole("cell")[1]).toHaveTextContent("0.003");
  });

  /**
   * Also mine. The band is what makes the chart readable as a *choice* — an alpha whose
   * neighbours sit inside it was not really chosen. Plotting `std_score` on its own axis
   * instead of around the mean draws a near-flat line at the bottom of the plot, which reads
   * as a well-separated optimum rather than as dispersion. The band has to be mean ± std.
   */
  it("draws the band at mean ± std rather than at the std on its own", () => {
    render(CrossValidationPanel, { props: { crossValidation: CV } });
    const series = pathOption().series;
    const upper = series.find((one) => one.name === "Mean + 1 std");
    const lower = series.find((one) => one.name === "Mean − 1 std");
    expect(upper?.data[1]).toBeCloseTo(0.501, 6);
    expect(lower?.data[1]).toBeCloseTo(0.495, 6);
  });

  it("names the y-axis after the metric the fit recorded, not a generic label", () => {
    render(CrossValidationPanel, { props: { crossValidation: CV } });
    expect(pathOption().yAxis.name).toBe("poisson-nloglik");
  });
});
