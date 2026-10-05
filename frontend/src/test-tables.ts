import { within } from "@testing-library/vue";

/**
 * Read a table cell by the **header above it**, rather than by its position in the row.
 *
 * Every existing table assertion in this repository indexes cells positionally —
 * `within(row).getAllByRole("cell")[2]` — and none relates a header to a cell. Two tests
 * (`PartitionTable.test.ts`, `DiagnosticsView.test.ts`) pin an exact header *sequence* with
 * `toEqual`, which catches a reordered `columns` prop; nothing catches the other half, a
 * row whose **values** are permuted under unchanged headers. A hand-written table enforces no
 * relation between its header row and its body cells, so that permutation renders every value
 * under the wrong heading, silently, and a positional assertion agrees with it. `ChartFigure`
 * closes the gap at compile time (RL-1307: each column carries its own accessor). This helper
 * is how a test compares a chart's table with the chart's data by label (PL-1286 acceptance 5).
 *
 * That is the failure mode a retrofit actually produces, because a retrofit's whole job is
 * transcribing an already-correct chart option into a `columns`/`rows` pair.
 *
 * Cells are located by **DOM order within the row**, not by role, deliberately: a
 * `ChartFigure` row's first cell is `<th scope="row">` (`rowheader`) and the rest are `<td>`
 * (`cell`), and a hand-written table may or may not name its rows the same way. Filtering by
 * role would shift every index by one between shapes, which is precisely the column shift this
 * helper exists to catch.
 */
export function cellUnder(
  table: HTMLElement,
  rowName: string | RegExp,
  columnName: string,
): HTMLElement {
  const headers = within(table)
    .getAllByRole("columnheader")
    .map((header) => header.textContent?.trim() ?? "");

  const column = headers.indexOf(columnName);
  if (column === -1) {
    throw new Error(
      `No column headed "${columnName}". This table has: ${headers.join(" | ")}`,
    );
  }

  const row = within(table).getByRole("row", { name: rowName });
  const cells = Array.from(row.querySelectorAll("td, th"));
  const cell = cells[column];
  if (!(cell instanceof HTMLElement)) {
    throw new Error(
      `Row ${String(rowName)} has ${cells.length} cells, so nothing sits under ` +
        `"${columnName}" (column ${column}). The row is shorter than the header row.`,
    );
  }
  return cell;
}
