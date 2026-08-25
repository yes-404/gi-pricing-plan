import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import { cellUnder } from "@/test-tables";

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

  describe("refuses a row that does not fit its headers", () => {
    // The guard is dev-only and would otherwise never print a failure in this repository,
    // which CLAUDE.md §13 says is the same as never having been tested. Each case below is
    // deliberately broken input, and each asserts the message, not merely that something
    // threw — the message is the whole value of the guard to a caller transcribing nine
    // tables by hand.
    function renderRows(rows: readonly (readonly (string | number | null)[])[]) {
      return () =>
        render(ChartFigure, {
          props: { title: "Lift by decile", columns: COLUMNS, rows },
          slots: { default: "<div data-testid='chart' />" },
        });
    }

    it("throws when a row is short, which would leave a header standing over nothing", () => {
      expect(renderRows([[1, 0.021]])).toThrow(
        /row 0 has 2 cells but there are 3 columns \(Bin \| Predicted \| Actual\)/,
      );
    });

    it("throws when a row is long, which would put a value under no header at all", () => {
      expect(renderRows([[1, 0.021, 0.023, 0.5]])).toThrow(/row 0 has 4 cells but there are 3/);
    });

    it("names which row, because a caller finding out that one of nine is wrong learns little", () => {
      expect(renderRows([[1, 0.021, 0.023], [2, 0.049, null], [3, 0.06]])).toThrow(
        /row 2 has 2 cells/,
      );
    });
  });

  describe("a value that sits under the wrong header", () => {
    // The other half of the same defect, and the half the arity guard is blind to by
    // construction: every row here is exactly three cells wide. `columns` and `rows` are
    // independent props, so the two can be permuted against each other from either side.
    const LABELLED = [["Decile 1", 0.021, 0.023]] as const;

    function table(
      columns: readonly string[],
      rows: readonly (readonly (string | number | null)[])[],
    ) {
      render(ChartFigure, {
        props: { title: "Lift by decile", columns, rows },
        slots: { default: "<div data-testid='chart' />" },
      });
      return screen.getByRole("table", { name: /lift by decile/i });
    }

    it("reads each cell by the header above it when the pair is correct", () => {
      const figure = table(COLUMNS, LABELLED);
      expect(cellUnder(figure, /Decile 1/, "Predicted")).toHaveTextContent("0.021");
      expect(cellUnder(figure, /Decile 1/, "Actual")).toHaveTextContent("0.023");
    });

    it("catches a row whose values are swapped under unchanged headers", () => {
      const figure = table(COLUMNS, [["Decile 1", 0.023, 0.021]]);
      // The arity guard did not fire — three cells, three columns — and the render succeeded.
      expect(within(figure).getAllByRole("row")).toHaveLength(2);
      expect(cellUnder(figure, /Decile 1/, "Predicted")).toHaveTextContent("0.023");
    });

    it("catches a reordered `columns` prop that a positional read agrees with", () => {
      // This is the case that makes the helper worth having rather than a longer way to
      // write an index. The rows are untouched and the headers moved, so cell 1 still holds
      // 0.021 and every positional assertion in this repository passes — while the table now
      // publishes the predicted value as the actual one. Only an assertion phrased in terms
      // of the pairing sees it.
      const figure = table(["Bin", "Actual", "Predicted"], LABELLED);
      const row = within(figure).getAllByRole("row")[1] as HTMLElement;
      expect(within(row).getAllByRole("cell")[1]).toHaveTextContent("0.021");
      expect(cellUnder(figure, /Decile 1/, "Predicted")).toHaveTextContent("0.023");
    });

    it("says what the table does have when asked for a header it does not", () => {
      const figure = table(COLUMNS, LABELLED);
      expect(() => cellUnder(figure, /Decile 1/, "Exposure")).toThrow(
        /No column headed "Exposure". This table has: Bin \| Predicted \| Actual/,
      );
    });
  });
});
