import { render, screen, within } from "@testing-library/vue";
import type { Component } from "vue";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { Column } from "@/chart-table";
import { cellUnder } from "@/test-tables";

import ChartFigure from "../ChartFigure.vue";

/**
 * `render()` infers a generic component's `T` as `unknown`, so it would refuse correctly typed
 * columns. Type checking of the generic is the `__typecheck__` fixtures' job. This file checks
 * what renders.
 */
const Figure: Component = ChartFigure;

interface Bin {
  readonly label: string | null;
  readonly predicted: number;
  readonly actual: number | null;
}

const ROWS: readonly Bin[] = [
  { label: "Decile 1", predicted: 0.021, actual: 0.023 },
  { label: "Decile 2", predicted: 0.049, actual: null },
];

const COLUMNS: readonly Column<Bin>[] = [
  { key: "bin", label: "Bin", value: (r) => r.label },
  { key: "predicted", label: "Predicted", value: (r) => r.predicted },
  { key: "actual", label: "Actual", value: (r) => r.actual },
];

function renderFigure(
  columns: readonly Column<Bin>[] = COLUMNS,
  rows: readonly Bin[] = ROWS,
) {
  return render(Figure, {
    props: { title: "Lift by decile", columns, rows },
    slots: { default: "<div data-testid='chart' />" },
  });
}

function table(): HTMLElement {
  return screen.getByRole("table", { name: /lift by decile/i });
}

describe("ChartFigure (NFR-463)", () => {
  it("renders the chart it was given", () => {
    renderFigure();
    expect(screen.getByTestId("chart")).toBeInTheDocument();
  });

  it("gives the table the figure's own name, so a screen reader can tell two apart", () => {
    renderFigure();
    expect(table()).toBeInTheDocument();
  });

  it("renders one header per column, labelled by the descriptor's label, and one row per datum", () => {
    renderFigure();
    const headers = within(table()).getAllByRole("columnheader").map((h) => h.textContent?.trim());
    expect(headers).toEqual(["Bin", "Predicted", "Actual"]);
    expect(within(table()).getAllByRole("row")).toHaveLength(ROWS.length + 1);
  });

  it("NFR-463: names each row by its first column, rendered as a row header", () => {
    renderFigure();
    const rowHeaders = within(table()).getAllByRole("rowheader");
    expect(rowHeaders).toHaveLength(ROWS.length);
    expect(rowHeaders.map((h) => h.textContent?.trim())).toEqual(["Decile 1", "Decile 2"]);
  });

  it("NFR-463: reads every cell from its own column's accessor", () => {
    renderFigure();
    expect(cellUnder(table(), /Decile 1/, "Predicted")).toHaveTextContent("0.021");
    expect(cellUnder(table(), /Decile 1/, "Actual")).toHaveTextContent("0.023");
    expect(cellUnder(table(), /Decile 2/, "Predicted")).toHaveTextContent("0.049");
  });

  it("NFR-463: a reordered columns prop moves each value with its heading", () => {
    // The case the positional shape got wrong: the headers moved and the values stayed.
    // With descriptors, a value travels with its own column.
    renderFigure([COLUMNS[0]!, COLUMNS[2]!, COLUMNS[1]!]);
    expect(cellUnder(table(), /Decile 1/, "Predicted")).toHaveTextContent("0.021");
    expect(cellUnder(table(), /Decile 1/, "Actual")).toHaveTextContent("0.023");
  });

  it("writes a missing value as an em dash rather than as a zero, in a cell and in a row header", () => {
    renderFigure(COLUMNS, [...ROWS, { label: null, predicted: 0.06, actual: 0.07 }]);
    expect(cellUnder(table(), /Decile 2/, "Actual")).toHaveTextContent("—");
    expect(cellUnder(table(), /Decile 2/, "Actual")).not.toHaveTextContent("0");
    const rowHeaders = within(table()).getAllByRole("rowheader");
    expect(rowHeaders[2]).toHaveTextContent("—");
  });

  it("renders the table for a chart with no data, and says so without naming a module", () => {
    renderFigure(COLUMNS, []);
    expect(within(table()).getAllByRole("row")).toHaveLength(1);
    expect(screen.getByText("No rows — this figure has no data to show.")).toBeInTheDocument();
  });

  describe("NFR-463: refuses two columns that share a key, in every build", () => {
    // RL-1307 item 5 (i): `key` is the Vue key and must be unique within one figure. Two
    // equal keys would let Vue patch one column's cells with the other's. The refusal must
    // not depend on a dev build: RL-1307 retired the arity guard because it was dev-only, so
    // the second case runs with DEV stubbed false, and a DEV gate fails it.
    afterEach(() => {
      vi.unstubAllEnvs();
    });

    const duplicate: readonly Column<Bin>[] = [
      COLUMNS[0]!,
      COLUMNS[1]!,
      { key: "predicted", label: "Actual", value: (r) => r.actual },
    ];

    it.each([
      ["as built", undefined],
      ["with DEV false, as in production", false],
    ] as const)("refuses two columns that share a key, %s", (_name, dev) => {
      if (dev !== undefined) vi.stubEnv("DEV", dev);
      renderFigure(duplicate);
      expect(screen.getByRole("alert")).toHaveTextContent(
        'Table unavailable: two columns in "Lift by decile" share the key "predicted" (bin | predicted | predicted).',
      );
      expect(screen.queryByRole("table")).toBeNull();
      expect(screen.getByTestId("chart")).toBeInTheDocument();
    });
  });

  it("accepts two columns with the same label under different keys", () => {
    // The (b′) half of RL-1307 item 3: a label is display text, so equal labels are allowed.
    renderFigure([
      COLUMNS[0]!,
      { key: "a", label: "Rate", value: (r) => r.predicted },
      { key: "b", label: "Rate", value: (r) => r.actual },
    ]);
    expect(within(table()).getAllByRole("columnheader")).toHaveLength(3);
  });
});
