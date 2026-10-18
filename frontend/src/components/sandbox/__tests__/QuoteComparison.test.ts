import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import type { ScoreComparison } from "@/api/score";

import QuoteComparison from "../QuoteComparison.vue";
import { formatAmount } from "../ladder";

// PL-1764 Task 3 (SL-1550, WK-675 lane C S7), with RL-1765 DP-2 (a): only diff.steps become
// rows, and the caption keeps "for this quote".

const COMPARISON: ScoreComparison = {
  base: {
    outcome: "quoted",
    rating_version_ref: "rating_version:motor-gb@3",
    bundle_hash: `sha256:${"c".repeat(64)}`,
    premium_ladder: [
      { rung: "risk_premium", value_minor: 50000 },
      { rung: "payable_premium", value_minor: 63000 },
    ],
  },
  comparison: {
    outcome: "declined",
    rating_version_ref: "rating_version:motor-gb@2",
    bundle_hash: `sha256:${"d".repeat(64)}`,
    premium_ladder: [
      { rung: "risk_premium", value_minor: 48000 },
      { rung: "payable_premium", value_minor: 60000 },
    ],
  },
  diff: {
    unchanged: 11,
    steps: [
      {
        step_id: "s_rate",
        change: "changed",
        own_change: true,
        changed_fields: ["produced"],
        base: { step_id: "s_rate", type: "table", label: "Rate", elapsed_us: 0, consumed: {}, produced: { rate: "1.10" } },
        comparison: { step_id: "s_rate", type: "table", label: "Rate", elapsed_us: 0, consumed: {}, produced: { rate: "1.20" } },
      },
      {
        step_id: "s_total",
        change: "changed",
        own_change: true,
        changed_fields: ["consumed", "produced"],
        base: { step_id: "s_total", type: "expression", label: "Total", elapsed_us: 0, consumed: { rate: "1.10" }, produced: { total: "110" } },
        comparison: { step_id: "s_total", type: "expression", label: "Total", elapsed_us: 0, consumed: { rate: "1.20" }, produced: { total: "125" } },
      },
      {
        step_id: "s_ipt",
        change: "changed",
        own_change: false,
        changed_fields: ["consumed", "produced"],
        base: { step_id: "s_ipt", type: "expression", label: "IPT", elapsed_us: 0, consumed: { total: "110" }, produced: { ipt: "13" } },
        comparison: { step_id: "s_ipt", type: "expression", label: "IPT", elapsed_us: 0, consumed: { total: "125" }, produced: { ipt: "15" } },
      },
      {
        step_id: "m_ncd__s_cap",
        change: "changed",
        own_change: true,
        changed_fields: ["consumed", "produced"],
        base: { step_id: "m_ncd__s_cap", type: "constraint", label: "Cap", elapsed_us: 0, consumed: { x: "1" }, produced: { cap: "5" } },
        comparison: { step_id: "m_ncd__s_cap", type: "constraint", label: "Cap", elapsed_us: 0, consumed: { x: "2" }, produced: { cap: "6" } },
      },
      {
        step_id: "s_new",
        change: "added",
        own_change: true,
        base: null,
        comparison: { step_id: "s_new", type: "expression", label: "Loading", elapsed_us: 0, consumed: {}, produced: { loading: "1.05" } },
      },
    ],
  },
};

function show(): void {
  render(QuoteComparison, { props: { comparison: COMPARISON } });
}

function rowOf(table: HTMLElement, id: string): HTMLElement | undefined {
  return within(table)
    .getAllByRole("row")
    .find((r) => r.textContent?.includes(id));
}

describe("QuoteComparison", () => {
  it("FR-262 B1 (PL-1286 item 8): an edited step whose input also moved names both causes", () => {
    show();
    const table = screen.queryByRole("table", { name: /Step differences/ });
    expect(table).not.toBeNull();
    const row = rowOf(table!, "s_total");
    expect(row).toBeDefined();
    expect(within(row!).getByText("Edited; its inputs also changed")).toBeInTheDocument();
    expect(within(row!).queryByText(/unchanged|not edited/i)).toBeNull();
  });

  it("FR-262 B2: a knock-on step reads 'Changed through its inputs'", () => {
    show();
    const table = screen.queryByRole("table", { name: /Step differences/ });
    expect(table).not.toBeNull();
    const row = rowOf(table!, "s_ipt");
    expect(row).toBeDefined();
    expect(within(row!).getByText("Changed through its inputs")).toBeInTheDocument();
    expect(within(row!).queryByText(/unchanged|not edited/i)).toBeNull();
  });

  it("FR-262 B3: an added step has an empty base and shows what the comparison produced", () => {
    show();
    const table = screen.queryByRole("table", { name: /Step differences/ });
    expect(table).not.toBeNull();
    const row = rowOf(table!, "s_new");
    expect(row).toBeDefined();
    expect(within(row!).getByText("Added in comparison")).toBeInTheDocument();
    const cells = Array.from(row!.querySelectorAll("td, th"));
    expect(cells[2]?.textContent?.trim()).toBe("—");
    expect(cells[3]?.textContent?.trim()).toBe('{"loading":"1.05"}');
  });

  it("FR-262 B4 (LG-1699:88): a mounted step's namespaced id is shown as it is", () => {
    show();
    const table = screen.queryByRole("table", { name: /Step differences/ });
    expect(table).not.toBeNull();
    const row = rowOf(table!, "m_ncd__s_cap");
    expect(row).toBeDefined();
    expect(row!.textContent).toContain("m_ncd__s_cap");
    expect(within(row!).getByText("Edited; its inputs also changed")).toBeInTheDocument();
  });

  it("FR-262 B5 (RL-1765 DP-2): the caption keeps 'for this quote' and only diff.steps become rows", () => {
    show();
    const table = screen.queryByRole("table", { name: /11 steps unchanged for this quote/ });
    expect(table).not.toBeNull();
    const bodyRows = Array.from(table!.querySelectorAll("tbody tr"));
    expect(bodyRows).toHaveLength(5);
    const order = ["s_rate", "s_total", "s_ipt", "m_ncd__s_cap", "s_new"];
    order.forEach((id, i) => {
      expect(bodyRows[i]?.textContent).toContain(id);
    });
  });

  it("FR-262 B6: a summary table shows both versions, both outcomes and both payable premiums", () => {
    show();
    const summary = screen.queryByRole("table", { name: "Both results" });
    expect(summary).not.toBeNull();
    expect(summary).toHaveTextContent("rating_version:motor-gb@3");
    expect(summary).toHaveTextContent("rating_version:motor-gb@2");
    expect(summary).toHaveTextContent("quoted");
    expect(summary).toHaveTextContent("declined");
    expect(summary).toHaveTextContent(formatAmount(63000));
    expect(summary).toHaveTextContent(formatAmount(60000));
  });
});
