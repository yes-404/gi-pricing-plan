import { render, screen } from "@testing-library/vue";
import { describe, expect, it, vi } from "vitest";

import type { OneWaySummary } from "@/api/profiles";

import OneWayChart from "../OneWayChart.vue";

// ECharts needs a real canvas and happy-dom has none. The stub keeps the one thing worth
// asserting on visible to the test: the option object the component computes. Mirrors
// `HistogramChart.test.ts`, which is the neighbour this component should have had a test
// beside since it landed.
vi.mock("vue-echarts", () => ({
  default: {
    name: "VChart",
    props: ["option"],
    template: "<div data-testid='chart'>{{ JSON.stringify(option) }}</div>",
  },
}));

type Series = {
  name: string;
  type: string;
  yAxisIndex: number;
  data: (number | null | (number | null)[])[];
};

type Option = {
  xAxis: { data: string[] };
  yAxis: { name: string; position: string }[];
  series: Series[];
};

function option(): Option {
  // `renderItem` is a function and does not survive `JSON.stringify`. Everything this file
  // asserts on is data, which does.
  return JSON.parse(screen.getByTestId("chart").textContent ?? "") as Option;
}

/**
 * Two levels, one of which has no interval.
 *
 * Annotated as `OneWaySummary`, not left a bare literal: the fixture is bound to the
 * generated contract, so a future rename in `model-schema` fails type-check here instead of
 * passing silently.
 */
function summary(): OneWaySummary {
  return {
    banding: "levels",
    column: "vehicle_age",
    rows: [
      {
        level: "0–3",
        exposure_years: "1234.56",
        claim_count: 90,
        claim_amount_minor: 450_000,
        frequency: 0.0729,
        frequency_ci: [0.0586, 0.0895],
        mean_severity: 5000,
        mean_burning_cost: 364.5,
      },
      {
        level: "4+",
        exposure_years: "12.5",
        claim_count: 1,
        claim_amount_minor: 20_000,
        frequency: 0.08,
        frequency_ci: null,
        mean_severity: 20_000,
        mean_burning_cost: 1600,
      },
    ],
  };
}

describe("OneWayChart", () => {
  it("pairs exposure against frequency on two axes", () => {
    render(OneWayChart, { props: { summary: summary() } });
    const chart = option();

    // The pairing is the point of a one-way: a level with a high frequency and almost no
    // exposure is noise. Bars and line on one axis each would hide exactly that.
    const exposure = chart.series.find((s) => s.name === "Exposure");
    const frequency = chart.series.find((s) => s.name === "Frequency");
    expect(exposure?.type).toBe("bar");
    expect(exposure?.yAxisIndex).toBe(0);
    expect(frequency?.type).toBe("line");
    expect(frequency?.yAxisIndex).toBe(1);
  });

  it("names each axis after what it carries, on the side it is drawn", () => {
    render(OneWayChart, { props: { summary: summary() } });
    const chart = option();

    expect(chart.yAxis.map((axis) => axis.name)).toEqual(["Exposure", "Frequency"]);
    expect(chart.yAxis.map((axis) => axis.position)).toEqual(["left", "right"]);
  });

  it("plots the exact decimal exposure as a number without disturbing the stored string", () => {
    const fixture = summary();
    render(OneWayChart, { props: { summary: fixture } });

    // `exposure_years` is an exact decimal **string** (FR-OVR-7). A chart coordinate is a
    // float64 either way and nothing computes with it, so `Number()` is safe here — this
    // asserts the conversion happens at the boundary and nowhere else.
    expect(option().series.find((s) => s.name === "Exposure")?.data).toEqual([1234.56, 12.5]);
    expect(fixture.rows[0]?.exposure_years).toBe("1234.56");
  });

  it("draws a whisker per level from the exact Poisson interval", () => {
    render(OneWayChart, { props: { summary: summary() } });
    const ci = option().series.find((s) => s.name === "Frequency CI");

    // FR-DATA-26's interval, encoded as [category index, low, high] against the frequency
    // axis. A frequency published without one invites a decision the count cannot support.
    expect(ci?.type).toBe("custom");
    expect(ci?.yAxisIndex).toBe(1);
    expect(ci?.data[0]).toEqual([0, 0.0586, 0.0895]);
  });

  it("says a level has no interval rather than drawing a zero-width one", () => {
    render(OneWayChart, { props: { summary: summary() } });
    const ci = option().series.find((s) => s.name === "Frequency CI");

    // The second level's `frequency_ci` is null. Dropping the row would misalign every
    // later whisker against its category; collapsing it to the point estimate would assert
    // an interval of zero width, which is the opposite of what a missing one means.
    expect(ci?.data).toHaveLength(2);
    expect(ci?.data[1]).toEqual([1, null, null]);
  });

  it("orders the category axis as the rows arrive", () => {
    render(OneWayChart, { props: { summary: summary() } });

    // Every series indexes into this axis positionally — the CI series literally encodes
    // the category as an integer — so a reordering here silently repairs to the wrong level.
    expect(option().xAxis.data).toEqual(["0–3", "4+"]);
  });

  it("says so plainly when the column has no stored one-way", () => {
    render(OneWayChart, { props: { summary: { banding: "levels", column: "vin", rows: [] } } });

    expect(screen.queryByTestId("chart")).toBeNull();
    expect(screen.getByText("This column has no stored one-way.")).toBeInTheDocument();
  });
});
