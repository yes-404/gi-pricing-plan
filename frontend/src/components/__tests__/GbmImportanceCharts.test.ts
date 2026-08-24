import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it, vi } from "vitest";

import { DIAGNOSTICS } from "@/views/__tests__/fixtures";

import GbmImportanceCharts from "../GbmImportanceCharts.vue";

vi.mock("vue-echarts", () => ({
  default: {
    name: "VChart",
    props: ["option"],
    template: "<div data-testid='chart'>{{ JSON.stringify(option) }}</div>",
  },
}));

const GBM = DIAGNOSTICS.gbm;

function props() {
  return {
    importances: GBM?.importances ?? [],
    permutationImportances: GBM?.permutation_importances ?? [],
    monotonicity: GBM?.monotonicity ?? [],
  };
}

describe("GbmImportanceCharts", () => {
  it("labels permutation importance as holdout, since that is what it measures", () => {
    render(GbmImportanceCharts, { props: props() });
    const table = screen.getByRole("table", { name: /permutation importance \(holdout\)/i });
    expect(table).toBeInTheDocument();
  });

  it("gives permutation importance no train column", () => {
    render(GbmImportanceCharts, { props: props() });
    const table = screen.getByRole("table", { name: /permutation importance \(holdout\)/i });
    const headers = within(table)
      .getAllByRole("columnheader")
      .map((h) => h.textContent?.trim().toLowerCase());
    expect(headers).not.toContain("train");
  });

  it("gives gain importance no train or holdout column either", () => {
    render(GbmImportanceCharts, { props: props() });
    const table = screen.getByRole("table", { name: /^feature importance/i });
    const headers = within(table)
      .getAllByRole("columnheader")
      .map((h) => h.textContent?.trim().toLowerCase());
    expect(headers).not.toContain("train");
    expect(headers).not.toContain("holdout");
  });

  it("carries the repeat count and seed, without which a degradation is not reproducible", () => {
    render(GbmImportanceCharts, { props: props() });
    const table = screen.getByRole("table", { name: /permutation importance \(holdout\)/i });
    const row = within(table).getByRole("row", { name: /vehicle_age/ });
    const cells = within(row).getAllByRole("cell");
    expect(cells[3]).toHaveTextContent("5");
    expect(cells[4]).toHaveTextContent("20260824");
  });

  it("writes a null cover as an em dash rather than as a zero", () => {
    render(GbmImportanceCharts, { props: props() });
    const table = screen.getByRole("table", { name: /^feature importance/i });
    const row = within(table).getByRole("row", { name: /driver_age/ });
    const cells = within(row).getAllByRole("cell");
    expect(cells[1]).toHaveTextContent("—");
    expect(cells[1]).not.toHaveTextContent("0");
  });

  /**
   * The factor is a `<th scope="row">` in this table and not a `<td>`, so it is a `rowheader`
   * and `getAllByRole("cell")` does not return it — the declared direction is cell 0 and the
   * magnitude is cell 1. The plan's indices were one further along, and its first lookup was
   * an unscoped `getByRole("row", {name: /driver_age/})` that matches a row in all three
   * tables on this component.
   */
  it("names a monotonicity breach and how large it was", () => {
    render(GbmImportanceCharts, { props: props() });
    const table = screen.getByRole("table", { name: /monotonicity/i });
    const breach = within(table).getByRole("row", { name: /driver_age/ });
    const cells = within(breach).getAllByRole("cell");
    expect(cells[0]).toHaveTextContent(/violated/i);
    expect(cells[1]).toHaveTextContent("0.0031");
  });

  /**
   * Mine, not the plan's. `worst_violation` defaults to `0.0` and is documented as "`0.0` when
   * the constraint holds" — so the magnitude column alone cannot distinguish a satisfied
   * constraint from a violated one, and only the `holds` flag can. A row that reported the
   * number without the word would read as a clean sweep for every factor in the table.
   */
  it("says a satisfied constraint holds, which its zero magnitude alone does not", () => {
    render(GbmImportanceCharts, { props: props() });
    const table = screen.getByRole("table", { name: /monotonicity/i });
    const clean = within(table).getByRole("row", { name: /vehicle_age/ });
    const cells = within(clean).getAllByRole("cell");
    expect(cells[0]).toHaveTextContent(/decreasing — holds/i);
    expect(cells[0]).not.toHaveTextContent(/violated/i);
  });
});
