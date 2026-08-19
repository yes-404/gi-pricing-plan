import { render, screen } from "@testing-library/vue";
import { describe, expect, it, vi } from "vitest";

import HistogramChart from "../HistogramChart.vue";

// ECharts needs a real canvas and happy-dom has none. The stub keeps the one thing worth
// asserting on visible to the test: the option object the component computes.
vi.mock("vue-echarts", () => ({
  default: {
    name: "VChart",
    props: ["option"],
    template: "<div data-testid='chart'>{{ JSON.stringify(option) }}</div>",
  },
}));

type Option = {
  xAxis: { data: string[] };
  yAxis: { name: string }[];
  series: { name: string; data: number[] }[];
};

function option(): Option {
  return JSON.parse(screen.getByTestId("chart").textContent ?? "") as Option;
}

describe("HistogramChart", () => {
  it("labels each bar with its bin interval", () => {
    render(HistogramChart, {
      props: { histogram: { edges: [0, 10, 20], counts: [3, 7], exposure: [] } },
    });
    const chart = option();

    // FR-DATA-48's edges array is one longer than its counts: two edges bound one bin.
    expect(chart.xAxis.data).toEqual(["0–10", "10–20"]);
    expect(chart.series[0]?.data).toEqual([3, 7]);
    // Nothing to weight the bars by, so no second series and no second axis.
    expect(chart.series).toHaveLength(1);
    expect(chart.yAxis).toHaveLength(1);
  });

  it("plots exposure when the histogram carries it", () => {
    render(HistogramChart, {
      props: { histogram: { edges: [0, 10, 20], counts: [3, 7], exposure: ["1.5", "9.25"] } },
    });
    const chart = option();

    expect(chart.series.map((s) => s.name)).toContain("Exposure");
    expect(chart.series[1]?.data).toEqual([1.5, 9.25]);
    expect(chart.yAxis.map((axis) => axis.name)).toEqual(["Rows", "Exposure"]);
  });
});
