import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it, vi } from "vitest";

import type { Histogram } from "@/api/profiles";

import { cellUnder } from "@/test-tables";

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

function table(): HTMLElement {
  return screen.getByRole("table", { name: /distribution of vehicle_age/i });
}

describe("HistogramChart", () => {
  it("labels each bar with its bin interval", () => {
    // Annotated, not a bare literal: the fixture is bound to the generated contract, so a
    // future rename in `model-schema` fails type-check here instead of passing silently.
    const histogram: Histogram = { edges: [0, 10, 20], counts: [3, 7], exposure: [] };
    render(HistogramChart, { props: { histogram, column: "vehicle_age" } });
    const chart = option();

    // FR-DATA-48's edges array is one longer than its counts: two edges bound one bin.
    expect(chart.xAxis.data).toEqual(["0–10", "10–20"]);
    expect(chart.series[0]?.data).toEqual([3, 7]);
    // Nothing to weight the bars by, so no second series and no second axis.
    expect(chart.series).toHaveLength(1);
    expect(chart.yAxis).toHaveLength(1);
  });

  it("plots exposure when the histogram carries it", () => {
    const histogram: Histogram = {
      edges: [0, 10, 20],
      counts: [3, 7],
      exposure: ["1.5", "9.25"],
    };
    render(HistogramChart, { props: { histogram, column: "vehicle_age" } });
    const chart = option();

    expect(chart.series.map((s) => s.name)).toContain("Exposure");
    expect(chart.series[1]?.data).toEqual([1.5, 9.25]);
    expect(chart.yAxis.map((axis) => axis.name)).toEqual(["Rows", "Exposure"]);
  });

  describe("the table beside it (NFR-OVR-10)", () => {
    it("names itself after the column, so a page of them is navigable", () => {
      // The Profile page renders one of these per column. `ChartFigure` labels its table
      // with the figure's title, so without the column name a screen-reader user gets a
      // list of identically-named tables.
      const histogram: Histogram = { edges: [0, 10], counts: [3], exposure: [] };
      render(HistogramChart, { props: { histogram, column: "vehicle_age" } });
      expect(table()).toBeInTheDocument();
    });

    it("says the same thing as the chart, bin for bin", () => {
      const histogram: Histogram = {
        edges: [0, 10, 20],
        counts: [3, 7],
        exposure: ["1.5", "9.25"],
      };
      render(HistogramChart, { props: { histogram, column: "vehicle_age" } });

      expect(
        within(table())
          .getAllByRole("columnheader")
          .map((header) => header.textContent?.trim()),
      ).toEqual(["Bin", "Rows", "Exposure"]);
      expect(cellUnder(table(), /0–10/, "Rows")).toHaveTextContent("3");
      expect(cellUnder(table(), /10–20/, "Rows")).toHaveTextContent("7");
    });

    it("keeps exposure as the exact decimal string the profile stored", () => {
      // The chart widens it to a float because a coordinate is one either way (FR-OVR-7).
      // The table has no such excuse, and a trailing zero lost here is a value the reader
      // cannot tell from a rounded one.
      const histogram: Histogram = { edges: [0, 10], counts: [3], exposure: ["9.250"] };
      render(HistogramChart, { props: { histogram, column: "vehicle_age" } });

      expect(cellUnder(table(), /0–10/, "Exposure")).toHaveTextContent("9.250");
      expect(option().series[1]?.data).toEqual([9.25]);
    });

    it("drops the Exposure column rather than dashing it when nothing was weighted", () => {
      // The chart drops the series and the second axis in this case, so the table drops the
      // column: an em dash would say the bin has an exposure of nothing, which is a
      // different claim from the histogram having no exposure at all. `columns` and `rows`
      // narrow together, which is the reactive case ChartFigure's arity guard covers — a
      // render at all here is evidence the guard did not fire.
      const histogram: Histogram = { edges: [0, 10, 20], counts: [3, 7], exposure: [] };
      render(HistogramChart, { props: { histogram, column: "vehicle_age" } });

      expect(
        within(table())
          .getAllByRole("columnheader")
          .map((header) => header.textContent?.trim()),
      ).toEqual(["Bin", "Rows"]);
      expect(() => cellUnder(table(), /0–10/, "Exposure")).toThrow(/No column headed/);
      expect(within(table()).queryAllByText("—")).toHaveLength(0);
    });
  });
});
