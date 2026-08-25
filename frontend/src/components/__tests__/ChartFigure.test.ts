import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import ChartFigure from "../ChartFigure.vue";

const COLUMNS = ["Bin", "Predicted", "Actual"] as const;
const ROWS = [
  [1, 0.021, 0.023],
  [2, 0.049, null],
] as const;

function renderFigure() {
  return render(ChartFigure, {
    props: { title: "Lift by decile", columns: COLUMNS, rows: ROWS },
    slots: { default: "<div data-testid='chart' />" },
  });
}

describe("ChartFigure", () => {
  it("renders the chart it was given", () => {
    renderFigure();
    expect(screen.getByTestId("chart")).toBeInTheDocument();
  });

  it("gives the table the figure's own name, so a screen reader can tell two apart", () => {
    renderFigure();
    expect(screen.getByRole("table", { name: /lift by decile/i })).toBeInTheDocument();
  });

  it("renders one header cell per column and one row per datum", () => {
    renderFigure();
    const table = screen.getByRole("table", { name: /lift by decile/i });
    expect(within(table).getAllByRole("columnheader")).toHaveLength(COLUMNS.length);
    expect(within(table).getAllByRole("row")).toHaveLength(ROWS.length + 1);
  });

  it("writes a missing value as an em dash rather than as a zero", () => {
    renderFigure();
    const table = screen.getByRole("table", { name: /lift by decile/i });
    const cells = within(within(table).getAllByRole("row")[2] as HTMLElement).getAllByRole("cell");
    expect(cells[2]).toHaveTextContent("—");
    expect(cells[2]).not.toHaveTextContent("0");
  });

  it("renders the table for a chart with no data at all, so the emptiness is readable", () => {
    render(ChartFigure, {
      props: { title: "Lift by decile", columns: COLUMNS, rows: [] },
      slots: { default: "<div data-testid='chart' />" },
    });
    const table = screen.getByRole("table", { name: /lift by decile/i });
    expect(within(table).getAllByRole("row")).toHaveLength(1);
    expect(screen.getByText(/no rows/i)).toBeInTheDocument();
  });
});
