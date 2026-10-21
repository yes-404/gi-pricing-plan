import userEvent from "@testing-library/user-event";
import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it, vi } from "vitest";

import type {
  AttributionItem,
  AttributionSummary,
  DislocationBand,
  DislocationMover,
  RungContribution,
  SegmentSlice,
} from "@/api/dislocationRuns";
import { cellUnder } from "@/test-tables";

import AttributionWaterfall from "../AttributionWaterfall.vue";
import ChangeHistogram from "../ChangeHistogram.vue";
import LargestMovers from "../LargestMovers.vue";
import SegmentGrid from "../SegmentGrid.vue";

vi.mock("vue-echarts", () => ({
  default: {
    name: "VChart",
    props: ["option"],
    template: "<div data-testid='chart'>{{ JSON.stringify(option) }}</div>",
  },
}));

function option(): {
  xAxis: { data: string[] };
  series: { name: string; data: (number | null)[] }[];
} {
  return JSON.parse(screen.getByTestId("chart").textContent ?? "{}");
}

const BANDS: DislocationBand[] = [
  { band: "< -5%", policies: 3, exposure_share: 0.25, mean_change_pct: -7.5 },
  { band: "-5% to +5%", policies: 0, exposure_share: 0, mean_change_pct: null },
  { band: "≥ +5%", policies: 9, exposure_share: 0.75, mean_change_pct: 12.34 },
];

describe("ChangeHistogram", () => {
  it("FR-263: draws every band in the run's order, an empty band included", () => {
    render(ChangeHistogram, { props: { bands: BANDS } });
    expect(option().xAxis.data).toEqual(["< -5%", "-5% to +5%", "≥ +5%"]);
    expect(option().series[0]?.data).toEqual([3, 0, 9]);
  });

  it("FR-263, NFR-463: the table says what the chart says, each value under its heading", () => {
    render(ChangeHistogram, { props: { bands: BANDS } });
    const table = screen.getByRole("table", { name: /change distribution/i });
    expect(cellUnder(table, /≥ \+5%/, "Policies")).toHaveTextContent("9");
    expect(cellUnder(table, /≥ \+5%/, "Mean change")).toHaveTextContent("12.34%");
    expect(cellUnder(table, /-5% to \+5%/, "Mean change")).toHaveTextContent("—");
  });
});

describe("SegmentGrid", () => {
  const SEGMENTS: SegmentSlice[] = [
    { factor: "region", level: "north", policies: 5, exposure_share: 0.4, mean_change_pct: 3.1 },
    { factor: "region", level: null, policies: 1, exposure_share: 0.1, mean_change_pct: null },
  ];
  const RUNGS: RungContribution[] = [
    { rung: "risk_premium", contribution_pct: 80 },
    { rung: "office_premium", contribution_pct: null },
  ];

  it("FR-264: slices by each Factor level and by the originating ladder rung", () => {
    render(SegmentGrid, { props: { segments: SEGMENTS, rungs: RUNGS } });
    const grid = screen.getByRole("table", { name: /change by segment/i });
    expect(cellUnder(grid, /north/, "Mean change")).toHaveTextContent("3.10%");
    expect(cellUnder(grid, /\(missing\)/, "Policies")).toHaveTextContent("1");
    const rungs = screen.getByRole("table", { name: /change by ladder rung/i });
    expect(cellUnder(rungs, /risk_premium/, "Contribution")).toHaveTextContent("80.00%");
    expect(option().xAxis.data).toEqual(["risk_premium", "office_premium"]);
  });

  it("FR-264: says so when the run declared no segments", () => {
    render(SegmentGrid, { props: { segments: [], rungs: [] } });
    expect(screen.getByText(/declared no segments/i)).toBeInTheDocument();
  });
});

describe("AttributionWaterfall", () => {
  const ITEMS: AttributionItem[] = [
    { group: "c1", shapley_minor: 600, isolated_minor: 650, cumulative_minor: 600, mean_change_pct: 6 },
    { group: "c2", shapley_minor: -200, isolated_minor: -180, cumulative_minor: 400, mean_change_pct: -2 },
  ];
  const SUMMARY: AttributionSummary = {
    method: "shapley",
    total_change_minor: 400,
    residual_minor: 0,
    order_sensitivity_lower_bound: null,
    residual_share: null,
    orders_sampled: null,
    subset_bundle_count: 4,
    subset_bundle_hashes: [],
    subset_valuation: "rerate",
    replay_fell_back: false,
  };

  it("FR-266: floats each group from the cumulative total before it", () => {
    render(AttributionWaterfall, { props: { items: ITEMS, summary: SUMMARY } });
    const series = option().series;
    expect(series.find((s) => s.name === "Base")?.data).toEqual([0, 400]);
    expect(series.find((s) => s.name === "Increase")?.data).toEqual([600, null]);
    expect(series.find((s) => s.name === "Decrease")?.data).toEqual([null, 200]);
  });

  it("FR-266, NFR-463: tabulates each group's change and cumulative total", () => {
    render(AttributionWaterfall, { props: { items: ITEMS, summary: SUMMARY } });
    const table = screen.getByRole("table", { name: /attribution/i });
    expect(cellUnder(table, /c2/, "Shapley change")).toHaveTextContent("-2.00");
    expect(cellUnder(table, /c2/, "Cumulative")).toHaveTextContent("4.00");
  });

  it("FR-266: under order_dependent the isolated amount is shown and the bound is stated", () => {
    const summary: AttributionSummary = {
      ...SUMMARY,
      method: "order_dependent",
      order_sensitivity_lower_bound: "0.100000",
      orders_sampled: 50,
    };
    const items = ITEMS.map((i) => ({ ...i, shapley_minor: null }));
    render(AttributionWaterfall, { props: { items, summary } });
    const table = screen.getByRole("table", { name: /attribution/i });
    expect(cellUnder(table, /c1/, "Isolated change")).toHaveTextContent("6.50");
    expect(screen.getByText("0.100000")).toBeInTheDocument();
  });

  it("FR-266: a run without attribution says so", () => {
    render(AttributionWaterfall, { props: { items: null, summary: null } });
    expect(screen.getByText(/carries no attribution/i)).toBeInTheDocument();
  });
});

describe("LargestMovers", () => {
  const MOVERS: DislocationMover[] = [
    {
      quote_id: "Q7",
      baseline_outcome: "quoted",
      candidate_outcome: "quoted",
      baseline_minor: 1000,
      candidate_minor: 1200,
      change_minor: 200,
      baseline_error_code: null,
      candidate_error_code: null,
      origin_rung: "risk_premium",
      change_pct: "20.000000",
      columns: { channel: "web", premium_in: 12 },
    },
  ];

  it("FR-263: shows each mover's change and the decimal string change_pct as sent", () => {
    render(LargestMovers, { props: { movers: MOVERS } });
    const table = screen.getByRole("table", { name: /largest movers/i });
    expect(cellUnder(table, /Q7/, "Change %")).toHaveTextContent("20.000000%");
    expect(cellUnder(table, /Q7/, "Change")).toHaveTextContent("2.00");
    expect(cellUnder(table, /Q7/, "Origin rung")).toHaveTextContent("risk_premium");
  });

  it("FR-263: drills down to the individual quote's portfolio columns", async () => {
    render(LargestMovers, { props: { movers: MOVERS } });
    expect(screen.queryByText("channel")).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /show quote Q7/i }));
    const detail = screen.getByText("channel").closest("dl") as HTMLElement;
    expect(within(detail).getByText("web")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /hide quote Q7/i })).toHaveAttribute(
      "aria-expanded",
      "true",
    );
  });

  it("FR-263: says so when nothing moved beyond the threshold", () => {
    render(LargestMovers, { props: { movers: [] } });
    expect(screen.getByText(/no policy moved/i)).toBeInTheDocument();
  });
});
