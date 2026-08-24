import { render, screen } from "@testing-library/vue";
import { describe, expect, it, vi } from "vitest";

import type { DoubleLift } from "@/api/comparisons";
import DoubleLiftChart from "@/components/DoubleLiftChart.vue";

// `HistogramChart.test.ts`'s precedent: mock the renderer and assert against the option
// object, because a canvas in happy-dom tells you nothing about what was plotted.
vi.mock("vue-echarts", () => ({
  default: {
    name: "VChart",
    props: ["option"],
    template: "<div data-testid='chart'>{{ JSON.stringify(option) }}</div>",
  },
}));

// Bins deliberately out of ascending prediction order and in ascending *ratio* order, which
// is the order `02` §4.11 says the server already produced.
const SERIES: DoubleLift = {
  baseline_ref: "model:motor-ad-frequency@7",
  challenger_ref: "model:motor-ad-frequency-gbm@2",
  weighting: "exposure",
  bins: [
    {
      bin: 1,
      rows: 16950,
      actual: 0.0491,
      baseline_predicted: 0.0523,
      challenger_predicted: 0.0447,
      exposure_years: "14203.400000",
    },
    {
      bin: 2,
      rows: 16950,
      actual: 0.0402,
      baseline_predicted: 0.0399,
      challenger_predicted: 0.0405,
      exposure_years: "14180.000000",
    },
    {
      bin: 3,
      rows: 16950,
      actual: 0.035,
      baseline_predicted: 0.031,
      challenger_predicted: 0.0372,
      exposure_years: "14150.000000",
    },
  ],
};

function option(): Record<string, unknown> {
  return JSON.parse(screen.getByTestId("chart").textContent ?? "{}");
}

describe("DoubleLiftChart", () => {
  // §4.11: bins are ordered by the RATIO of the two predictions, and sorting by either
  // prediction "gives two lift curves side by side, which answers a different and much weaker
  // question". A re-sort here would substitute that question silently.
  it("plots the bins in the order the artifact gave them", () => {
    render(DoubleLiftChart, { props: { series: SERIES } });
    const opt = option() as unknown as {
      xAxis: { data: string[] };
      series: { name?: string; data: number[] }[];
    };
    expect(opt.xAxis.data).toEqual(["1", "2", "3"]);
    const baseline = opt.series.find((s) => s.name === "Baseline predicted");
    expect(baseline?.data).toEqual([0.0523, 0.0399, 0.031]);
  });

  it("plots actual, baseline and challenger as three separate series", () => {
    render(DoubleLiftChart, { props: { series: SERIES } });
    const names = (option().series as { name: string }[]).map((s) => s.name);
    expect(names).toContain("Actual");
    expect(names).toContain("Baseline predicted");
    expect(names).toContain("Challenger predicted");
  });

  // NFR-OVR-10 is WCAG 2.2 AA. Three lines separable only by hue fail for a reader who cannot
  // distinguish them, so line type carries the same information.
  it("distinguishes the three series by line type as well as colour", () => {
    render(DoubleLiftChart, { props: { series: SERIES } });
    const lines = (
      option().series as { type: string; lineStyle?: { type?: string } }[]
    ).filter((s) => s.type === "line");
    const types = lines.map((s) => s.lineStyle?.type ?? "solid");
    expect(new Set(types).size).toBe(lines.length);
  });

  // `exposure_years` is a DecimalStr — a string on the wire (FR-OVR-7's exact-decimal type).
  // It must reach ECharts as a number or the bars silently do not draw.
  it("converts the decimal-string exposure to numbers", () => {
    render(DoubleLiftChart, { props: { series: SERIES } });
    const exposure = (option().series as { name: string; data: unknown[] }[]).find(
      (s) => s.name === "Exposure",
    );
    expect(exposure?.data).toEqual([14203.4, 14180, 14150]);
  });

  // The same field is nullable, and a partly-populated exposure would draw a bar chart with
  // silent holes in it. Omit the series rather than plot a hole.
  it("omits the exposure series when any bin is missing it", () => {
    const partial: DoubleLift = {
      ...SERIES,
      bins: SERIES.bins.map((b, i) => (i === 1 ? { ...b, exposure_years: null } : b)),
    };
    render(DoubleLiftChart, { props: { series: partial } });
    const names = (option().series as { name: string }[]).map((s) => s.name);
    expect(names).not.toContain("Exposure");
  });
});
