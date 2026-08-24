import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it, vi } from "vitest";

import { partitions } from "@/api/diagnostics";
import { DIAGNOSTICS } from "@/views/__tests__/fixtures";

import LiftChart from "../LiftChart.vue";

vi.mock("vue-echarts", () => ({
  default: {
    name: "VChart",
    props: ["option"],
    template: "<div data-testid='chart'>{{ JSON.stringify(option) }}</div>",
  },
}));

type Option = { xAxis: { data: string[] }; series: { name: string; data: (number | null)[] }[] };

function option(): Option {
  return JSON.parse(screen.getByTestId("chart").textContent ?? "{}") as Option;
}

describe("LiftChart", () => {
  it("plots predicted and actual for each partition — four series, not two", () => {
    render(LiftChart, { props: { partitions: partitions(DIAGNOSTICS.universal) } });
    expect(option().series.map((s) => s.name)).toEqual([
      "Train predicted",
      "Train actual",
      "Holdout predicted",
      "Holdout actual",
    ]);
  });

  it("orders bins ascending, so the curve reads left to right", () => {
    render(LiftChart, { props: { partitions: partitions(DIAGNOSTICS.universal) } });
    expect(option().xAxis.data).toEqual(["1", "2"]);
  });

  it("tabulates rows per bin, because a decile on few rows is not a decile", () => {
    render(LiftChart, { props: { partitions: partitions(DIAGNOSTICS.universal) } });
    const table = screen.getByRole("table", { name: /lift by decile/i });
    const row = within(table).getAllByRole("row")[1] as HTMLElement;
    expect(within(row).getAllByRole("cell").map((c) => c.textContent?.trim())).toEqual([
      "1",
      "40753",
      "0.021",
      "0.023",
      "16950",
      "0.022",
      "0.025",
    ]);
  });
});
