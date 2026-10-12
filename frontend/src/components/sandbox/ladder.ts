import type { LadderRung } from "@/api/score";

type Operation = NonNullable<LadderRung["operation"]>;

export interface RungChange {
  readonly rung: LadderRung;
  /** This rung's value minus the previous rung's, in minor units; `null` for the first. */
  readonly change: number | null;
  /** Height of the invisible base under the floating bar. */
  readonly base: number;
  /** Height of the visible bar. */
  readonly size: number;
  /** The first and last rungs are drawn whole; the rest float by their change. */
  readonly kind: "total" | "increase" | "decrease";
}

/**
 * Turn the rungs into the rows the waterfall draws and the table lists.
 *
 * Subtraction here is on the integer minor-unit values the result already carries, for
 * display only; the exact replay is the engine's (FR-248), and nothing here recomputes a price.
 */
export function rungChanges(rungs: readonly LadderRung[]): RungChange[] {
  return rungs.map((rung, index) => {
    const previous = index === 0 ? null : (rungs[index - 1] as LadderRung).value_minor;
    const change = previous === null ? null : rung.value_minor - previous;
    const whole = index === 0 || index === rungs.length - 1;
    if (whole || change === null) {
      return { rung, change, base: 0, size: rung.value_minor, kind: "total" as const };
    }
    return {
      rung,
      change,
      base: Math.min(previous as number, rung.value_minor),
      size: Math.abs(change),
      kind: change >= 0 ? ("increase" as const) : ("decrease" as const),
    };
  });
}

/** The recorded operation (FR-248) in words, operands exactly as the platform sent them. */
export function describeOperation(operation: Operation | null | undefined): string {
  if (!operation) return "";
  switch (operation.kind) {
    case "multiply":
      return `× ${operation.factor ?? "?"}`;
    case "divide":
      return `÷ ${operation.divisor ?? "?"}`;
    case "add":
      return `+ ${operation.amount_unrounded_minor ?? operation.amount_minor ?? "?"}`;
    case "clamp":
      return operation.bound
        ? `clamp to ${operation.bound} ${operation.bound_unrounded_minor ?? ""}`.trim()
        : "clamp";
    case "round":
      return `round ${operation.mode ?? ""} to ${operation.dp ?? "?"} dp`.replace("  ", " ");
    case "none":
      return "no change";
  }
}
