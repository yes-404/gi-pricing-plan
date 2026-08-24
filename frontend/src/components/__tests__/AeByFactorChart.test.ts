import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it, vi } from "vitest";

import { partitions } from "@/api/diagnostics";
import { DIAGNOSTICS } from "@/views/__tests__/fixtures";

import AeByFactorChart from "../AeByFactorChart.vue";

// `HistogramChart.test.ts`'s precedent: mock the renderer and assert against the option
// object, because a canvas in the test DOM tells you nothing about what was plotted.
vi.mock("vue-echarts", () => ({
  default: {
    name: "VChart",
    props: ["option"],
    template: "<div data-testid='chart'>{{ JSON.stringify(option) }}</div>",
  },
}));

type Option = {
  xAxis: { data: string[] };
  series: { name: string; data: (number | null)[]; lineStyle?: { type?: string } }[];
};

function option(): Option {
  return JSON.parse(screen.getByTestId("chart").textContent ?? "{}") as Option;
}

function renderChart() {
  return render(AeByFactorChart, { props: { partitions: partitions(DIAGNOSTICS.universal) } });
}

describe("AeByFactorChart", () => {
  it("plots one series per partition, named for it", () => {
    renderChart();
    expect(option().series.map((s) => s.name)).toEqual(["Train", "Holdout"]);
  });

  it("plots the A/E ratio, not the actual and not the expected", () => {
    renderChart();
    const train = option().series.find((s) => s.name === "Train");
    expect(train?.data).toEqual([1.034, 0.96]);
  });

  it("keys the axis by factor and level together, since a level name is not unique", () => {
    renderChart();
    expect(option().xAxis.data).toEqual(["vehicle_age · 0-3", "vehicle_age · 4-9"]);
  });

  it("distinguishes the two series by line type as well as by hue", () => {
    renderChart();
    const types = option().series.map((s) => s.lineStyle?.type ?? "solid");
    expect(new Set(types).size).toBe(types.length);
  });

  it("carries exposure into the table, because an A/E on no exposure is noise", () => {
    renderChart();
    const table = screen.getByRole("table", { name: /a\/e by factor/i });
    const row = within(table).getByRole("row", { name: /0-3/ });
    expect(within(row).getAllByRole("cell").map((c) => c.textContent?.trim())).toEqual([
      "vehicle_age · 0-3",
      "1.034",
      "12034.5",
      "1.068",
      "5010.75",
    ]);
  });
});
