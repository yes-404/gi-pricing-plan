import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it, vi } from "vitest";

import type { LadderRung } from "@/api/score";

import LadderWaterfall from "../LadderWaterfall.vue";

vi.mock("vue-echarts", () => ({
  default: {
    name: "VChart",
    props: ["option"],
    template: "<div data-testid='chart'>{{ JSON.stringify(option) }}</div>",
  },
}));

const RUNGS: LadderRung[] = [
  { rung: "risk_premium", value_minor: 50000, components: { frequency: 20000, severity: 30000 } },
  { rung: "office_premium", value_minor: 60000, operation: { kind: "divide", divisor: "0.833333" } },
  { rung: "instalment_loading", value_minor: 63000, operation: { kind: "multiply", factor: "1.05" } },
  { rung: "payable_premium", value_minor: 63000, operation: { kind: "round", mode: "half_even", dp: 0 } },
];

function option(): { xAxis: { data: string[] } } {
  return JSON.parse(screen.getByTestId("chart").textContent ?? "{}") as { xAxis: { data: string[] } };
}

describe("LadderWaterfall", () => {
  it("draws every rung the result carries, including the optional instalment_loading (FR-252)", () => {
    render(LadderWaterfall, { props: { rungs: RUNGS } });
    expect(option().xAxis.data).toEqual([
      "risk_premium",
      "office_premium",
      "instalment_loading",
      "payable_premium",
    ]);
  });

  it("omits instalment_loading when the algorithm does not mount it", () => {
    render(LadderWaterfall, {
      props: { rungs: RUNGS.filter((r) => r.rung !== "instalment_loading") },
    });
    expect(option().xAxis.data).not.toContain("instalment_loading");
  });

  it("tabulates value, change and operation for every rung (NFR-463)", () => {
    render(LadderWaterfall, { props: { rungs: RUNGS } });
    const table = screen.getByRole("table", { name: /premium ladder/i });
    const row = within(table).getByRole("row", { name: /office_premium/ });
    expect(row).toHaveTextContent("600.00");
    expect(row).toHaveTextContent("100.00");
    expect(row).toHaveTextContent("÷ 0.833333");
  });

  it("OQ-551: shows no currency symbol and says the currency is not configured", () => {
    const { container } = render(LadderWaterfall, { props: { rungs: RUNGS } });
    expect(container.textContent).not.toMatch(/[£€$]/);
    expect(container.textContent).toMatch(/currency not configured \(OQ-551\)/);
  });

  it("FR-249 (R6.1, OQ-1460): shows no per-peril components, even if a rung carries the field", () => {
    const { container } = render(LadderWaterfall, { props: { rungs: RUNGS } });
    expect(container.textContent).not.toMatch(/frequency|severity|component/i);
    expect(JSON.stringify(option())).not.toMatch(/frequency|severity|components/);
  });
});
