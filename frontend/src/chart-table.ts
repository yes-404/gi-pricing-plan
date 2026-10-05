/**
 * The column descriptor `ChartFigure` takes (RL-1307, OQ-550 (c)).
 *
 * Each column carries its own accessor, so a table cell is read from the caller's own row
 * by the column it sits under. A value cannot be placed under a heading it does not belong
 * to without the accessor itself being wrong, and `vue-tsc` checks the accessor against the
 * row type. `key` is an identifier, unique within one figure. `label` is the heading text,
 * free to change.
 */
export type Cell = string | number | null;

export interface Column<R> {
  readonly key: string;
  readonly label: string;
  readonly value: (row: R) => Cell;
}
