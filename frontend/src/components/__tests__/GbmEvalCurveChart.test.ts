import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it, vi } from "vitest";

import { DIAGNOSTICS } from "@/views/__tests__/fixtures";

import GbmEvalCurveChart from "../GbmEvalCurveChart.vue";

vi.mock("vue-echarts", () => ({
  default: {
    name: "VChart",
    props: ["option"],
    template: "<div data-testid='chart'>{{ JSON.stringify(option) }}</div>",
  },
}));

function option(): {
  xAxis: { data: string[] };
  yAxis: { name: string };
  series: { name: string; data: (number | null)[]; lineStyle?: { type?: string } }[];
} {
  return JSON.parse(screen.getByTestId("chart").textContent ?? "{}");
}

const CURVE = DIAGNOSTICS.gbm?.eval_curve ?? [];

describe("GbmEvalCurveChart", () => {
  it("plots train and holdout as two series — the split this chart exists for", () => {
    render(GbmEvalCurveChart, { props: { evalCurve: CURVE } });
    expect(option().series.map((s) => s.name)).toEqual(["Train", "Holdout"]);
    expect(option().series[0]?.data).toEqual([0.512, 0.487, 0.471]);
    expect(option().series[1]?.data).toEqual([0.518, 0.499, 0.498]);
  });

  it("names the y-axis after the metric the fit recorded, not a generic label", () => {
    render(GbmEvalCurveChart, { props: { evalCurve: CURVE } });
    expect(option().yAxis.name).toBe("poisson-nloglik");
  });

  it("carries a gap in one series through as null rather than closing the line", () => {
    const sparse = CURVE.map((point, index) => (index === 1 ? { ...point, train: null } : point));
    render(GbmEvalCurveChart, { props: { evalCurve: sparse } });
    expect(option().series[0]?.data).toEqual([0.512, null, 0.471]);
  });

  it("distinguishes the two series by line type as well as by hue", () => {
    render(GbmEvalCurveChart, { props: { evalCurve: CURVE } });
    const types = option().series.map((s) => s.lineStyle?.type ?? "solid");
    expect(new Set(types).size).toBe(types.length);
  });

  it("tabulates one row per iteration with both partitions", () => {
    render(GbmEvalCurveChart, { props: { evalCurve: CURVE } });
    const table = screen.getByRole("table", { name: /evaluation curve/i });
    expect(within(table).getAllByRole("row")).toHaveLength(CURVE.length + 1);
  });

  /**
   * Mine, not the plan's. The x-axis is what tells a reader *which* iteration to stop at, and
   * `iteration` is a declared field rather than the array index — `GbmEvalPoint.iteration` is
   * `int >= 0` and nothing in the contract says the curve is dense or zero-based. A chart that
   * silently labelled position 0..n would report the wrong stopping point for any curve
   * recorded at an interval, which is the normal shape for a long boosting run.
   */
  it("labels the x-axis with the recorded iteration, not the position in the array", () => {
    const sampled = CURVE.map((point, index) => ({ ...point, iteration: index * 50 }));
    render(GbmEvalCurveChart, { props: { evalCurve: sampled } });
    expect(option().xAxis.data).toEqual(["0", "50", "100"]);
  });
});
