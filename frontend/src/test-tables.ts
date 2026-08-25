import { within } from "@testing-library/vue";

/**
 * Read a table cell by the **header above it**, rather than by its position in the row.
 *
 * Every existing table assertion in this repository indexes cells positionally —
 * `within(row).getAllByRole("cell")[2]` — and none relates a header to a cell. Two tests
 * (`PartitionTable.test.ts`, `DiagnosticsView.test.ts`) pin an exact header *sequence* with
 * `toEqual`, which catches a reordered `columns` prop; nothing catches the other half, a
 * row whose **values** are permuted under unchanged headers. `ChartFigure` takes `columns`
 * and `rows` as two independent props with no relation enforced between them, so that
 * permutation renders every value under the wrong heading, silently, and a positional
 * assertion agrees with it.
 *
 * That is the failure mode a retrofit actually produces, because a retrofit's whole job is
 * transcribing an already-correct chart option into a `columns`/`rows` pair.
 *
 * Cells are located by **DOM order within the row**, not by role, deliberately: a
 * `ChartFigure` row is all `<td>` (`cell`) while a hand-written table's first column is
 * often `<th scope="row">` (`rowheader`). Filtering by role would shift every index by one
 * between the two shapes — which is precisely the column shift this helper exists to catch.
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
        `"${columnName}" (column ${column}). A short row is the arity failure ` +
        `ChartFigure's own guard should have caught first.`,
    );
  }
  return cell;
}
