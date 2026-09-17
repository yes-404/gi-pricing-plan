import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it, vi } from "vitest";

import type { DoubleLift } from "@/api/comparisons";
import DoubleLiftChart from "@/components/DoubleLiftChart.vue";
import { cellUnder } from "@/test-tables";

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

  // NFR-463 is WCAG 2.2 AA. Three lines separable only by hue fail for a reader who cannot
  // distinguish them, so line type carries the same information.
  it("distinguishes the three series by line type as well as colour", () => {
    render(DoubleLiftChart, { props: { series: SERIES } });
    const lines = (
      option().series as { type: string; lineStyle?: { type?: string } }[]
    ).filter((s) => s.type === "line");
    const types = lines.map((s) => s.lineStyle?.type ?? "solid");
    expect(new Set(types).size).toBe(lines.length);
  });

  // `exposure_years` is a DecimalStr — a string on the wire (FR-10's exact-decimal type).
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

  describe("the table beside it (NFR-463)", () => {
    function table(series: DoubleLift = SERIES): HTMLElement {
      render(DoubleLiftChart, { props: { series } });
      return screen.getByRole("table", {
        name: /baseline against model:motor-ad-frequency-gbm@2/i,
      });
    }

    function headers(t: HTMLElement): string[] {
      return within(t)
        .getAllByRole("columnheader")
        .map((h) => h.textContent?.trim() ?? "");
    }

    // The comparison page renders one of these per challenger. A title of "Double lift"
    // would leave a screen-reader user a page of identically-named tables with no way to
    // tell which challenger each belongs to — the failure mode `HistogramChart`'s required
    // `column` prop exists to prevent, here solved for free because the challenger's ref is
    // already on the series.
    it("names itself after the challenger, not just after the chart type", () => {
      expect(table()).toBeInTheDocument();
    });

    // A column per plotted series, named as the legend names it: a reader moving between
    // chart and table should not have to match "Baseline predicted" against a shortening.
    it("gives each plotted series its own column, named as the legend names it", () => {
      const heads = headers(table());
      const plotted = (option().series as { name: string }[]).map((s) => s.name);
      for (const name of plotted) expect(heads).toContain(name);
    });

    it("says the same thing the chart plots, bin for bin", () => {
      const t = table();
      const opt = option() as unknown as { series: { name: string; data: number[] }[] };
      for (const name of ["Actual", "Baseline predicted", "Challenger predicted"]) {
        const plotted = opt.series.find((s) => s.name === name)?.data ?? [];
        SERIES.bins.forEach((bin, i) => {
          expect(cellUnder(t, new RegExp(`^${bin.bin} `), name)).toHaveTextContent(
            String(plotted[i]),
          );
        });
      }
    });

    // FR-10: the chart widens the decimal string because a coordinate is a float64 either
    // way; the table has no such excuse, and "14203.400000" losing its trailing zeros is a
    // recorded value the reader can no longer tell apart from a rounded one.
    it("keeps exposure as the exact decimal string the artifact recorded", () => {
      const t = table();
      expect(cellUnder(t, /^1 /, "Exposure")).toHaveTextContent("14203.400000");
      const plotted = (option().series as { name: string; data: number[] }[]).find(
        (s) => s.name === "Exposure",
      );
      expect(plotted?.data[0]).toBe(14203.4);
    });

    // `rows` is on the artifact and plotted by nothing. A sighted reader infers volume from
    // the exposure bars; with exposure absent — and it is all-or-nothing — a `rows`-less
    // table would say nothing about how much of the book each bin holds, which is what
    // decides whether a divergence between the two models matters at all.
    it("tables the row counts the chart does not plot, exposure or no exposure", () => {
      expect(cellUnder(table(), /^1 /, "Rows")).toHaveTextContent("16950");
      expect((option().series as { name: string }[]).map((s) => s.name)).not.toContain("Rows");
    });

    // The column narrows with the series. A column of em dashes would claim each bin has an
    // exposure of nothing, which is a different statement from the artifact carrying no
    // exposure at all.
    it("drops the Exposure column exactly when the chart drops the series", () => {
      const partial: DoubleLift = {
        ...SERIES,
        bins: SERIES.bins.map((b, i) => (i === 1 ? { ...b, exposure_years: null } : b)),
      };
      const heads = headers(table(partial));
      expect(heads).not.toContain("Exposure");
      expect(heads).toEqual([
        "Bin (by prediction ratio)",
        "Rows",
        "Actual",
        "Baseline predicted",
        "Challenger predicted",
      ]);
    });
  });
});
