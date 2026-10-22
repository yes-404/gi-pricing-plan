import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it, vi } from "vitest";

import type { ObjectivePreviewCurve } from "@/api/objectives";
import { cellUnder } from "@/test-tables";

import ObjectiveLossCurve from "../ObjectiveLossCurve.vue";

// SL-1275 (WK-690 Slice 5): the loss-curve preview is a `ChartFigure` in RL-1307's
// column-descriptor form, with its accessible table (PL-1621 5.4, NFR-463). The points come
// from the preview route's curve (RL-1616: "the curve equals compile_kernel's output"); this
// component only draws them. Row field names are PROVISIONAL until PL-1665 5.1' generates
// the preview shape, at which point `CURVE` takes its generated type.
vi.mock("vue-echarts", () => ({
  default: {
    name: "VChart",
    props: ["option"],
    template: "<div data-testid='chart'>{{ JSON.stringify(option) }}</div>",
  },
}));

const CURVE: ObjectivePreviewCurve = {
  f: [-1, 0, 1],
  loss: [4.25, 1.5, 0.75],
  gradient: [-3, -1, 0],
  hessian: [2, 2, 2],
};

function option(): { xAxis: { data: string[] }; series: { name: string; data: number[] }[] } {
  return JSON.parse(screen.getByTestId("chart").textContent ?? "{}");
}

describe("ObjectiveLossCurve", () => {
  it("plots the loss at each grid point the route returned, untouched", () => {
    render(ObjectiveLossCurve, { props: { curve: CURVE } });

    expect(option().series).toHaveLength(1);
    expect(option().series[0]?.data).toEqual([4.25, 1.5, 0.75]);
    expect(option().xAxis.data).toEqual(["-1", "0", "1"]);
  });

  it("NFR-463: tabulates every plotted point, each value under its own heading", () => {
    render(ObjectiveLossCurve, { props: { curve: CURVE } });

    const table = screen.getByRole("table", { name: /loss curve/i });
    expect(within(table).getAllByRole("row")).toHaveLength(CURVE.f.length + 1);
    expect(cellUnder(table, /^0\s/, "Loss")).toHaveTextContent("1.5");
    expect(cellUnder(table, /^1\s/, "Loss")).toHaveTextContent("0.75");
  });

  it("shows a non-finite point the route reported as null as a gap, not a number", () => {
    render(ObjectiveLossCurve, {
      props: { curve: { ...CURVE, loss: [null, 1.5, 0.75] } },
    });

    expect(option().series[0]?.data).toEqual([null, 1.5, 0.75]);
    expect(cellUnder(screen.getByRole("table", { name: /loss curve/i }), /^-1\s/, "Loss")).toHaveTextContent("—");
  });

  it("keeps the table in the DOM beside the chart, not behind a disclosure", () => {
    const { container } = render(ObjectiveLossCurve, { props: { curve: CURVE } });

    expect(container.querySelector("details")).toBeNull();
    expect(screen.getByRole("table", { name: /loss curve/i })).toBeVisible();
  });
});
