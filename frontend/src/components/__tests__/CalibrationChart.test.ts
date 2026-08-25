import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it, vi } from "vitest";

import { partitions } from "@/api/diagnostics";
import { DIAGNOSTICS } from "@/views/__tests__/fixtures";

import CalibrationChart from "../CalibrationChart.vue";

vi.mock("vue-echarts", () => ({
  default: {
    name: "VChart",
    props: ["option"],
    template: "<div data-testid='chart'>{{ JSON.stringify(option) }}</div>",
  },
}));

type Option = {
  xAxis: { type: string };
  series: { name: string; type: string; data: unknown[] }[];
};

function option(): Option {
  return JSON.parse(screen.getByTestId("chart").textContent ?? "{}") as Option;
}

describe("CalibrationChart", () => {
  it("plots predicted against actual as points, not against the bin index", () => {
    render(CalibrationChart, { props: { partitions: partitions(DIAGNOSTICS.universal) } });
    expect(option().xAxis.type).toBe("value");
    const train = option().series.find((s) => s.name === "Train");
    expect(train?.type).toBe("scatter");
    expect(train?.data).toEqual([
      [0.021, 0.023],
      [0.049, 0.047],
    ]);
  });

  it("draws the perfect-calibration diagonal, which is what the points are read against", () => {
    render(CalibrationChart, { props: { partitions: partitions(DIAGNOSTICS.universal) } });
    expect(option().series.some((s) => s.name === "Perfect calibration")).toBe(true);
  });

  it("tabulates each bin's predicted and actual per partition", () => {
    render(CalibrationChart, { props: { partitions: partitions(DIAGNOSTICS.universal) } });
    const table = screen.getByRole("table", { name: /calibration by decile/i });
    expect(within(table).getAllByRole("row")).toHaveLength(3);
  });
});
