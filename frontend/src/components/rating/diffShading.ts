/**
 * How one changed cell is shaded on the diff view (FR-231, `03` §5.3): by the size of its
 * relative change, with the direction also written out. Shade is a heat step 0 to 4; it is a
 * display bucket only, so `Number` is read here and never carried into a price. The label keeps
 * the decimal string as the platform sent it (FR-10).
 */

export interface Shade {
  /** `none` for a cell with no relative change to show (absent baseline, or exactly zero). */
  direction: "up" | "down" | "none";
  /** 0 (none) to 4 (the largest). */
  step: 0 | 1 | 2 | 3 | 4;
  /** The text shown: the sign, the percentage as sent, or a dash where there is none. */
  label: string;
}

/** Upper bounds, in percent, of steps 1 to 3; anything above the last is step 4. */
const BOUNDS = [1, 5, 10] as const;

export function shadeChange(relChangePct: string | null): Shade {
  if (relChangePct === null) return { direction: "none", step: 0, label: "—" };
  const size = Math.abs(Number(relChangePct));
  if (size === 0) return { direction: "none", step: 0, label: "0%" };
  const rising = !relChangePct.startsWith("-");
  const bucket = BOUNDS.findIndex((bound) => size < bound);
  const step = (bucket === -1 ? 4 : bucket + 1) as Shade["step"];
  return {
    direction: rising ? "up" : "down",
    step,
    label: `${rising ? "+" : ""}${relChangePct}%`,
  };
}
