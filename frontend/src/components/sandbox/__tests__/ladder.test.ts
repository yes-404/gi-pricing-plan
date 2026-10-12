import { describe, expect, it } from "vitest";

import type { LadderRung } from "@/api/score";

import { describeOperation, formatAmount, rungChanges } from "../ladder";

const RUNGS: LadderRung[] = [
  { rung: "risk_premium", value_minor: 50000 },
  { rung: "expense_loading", value_minor: 55000, operation: { kind: "multiply", factor: "1.1" } },
  { rung: "constraints", value_minor: 54000, operation: { kind: "clamp", bound: "max", bound_unrounded_minor: "54000" } },
  { rung: "payable_premium", value_minor: 54000, operation: { kind: "round", mode: "half_even", dp: 0 } },
];

describe("the ladder's waterfall rows (FR-247, FR-248)", () => {
  it("draws the first and last rungs whole and floats the rest by their change", () => {
    const rows = rungChanges(RUNGS);
    expect(rows.map((r) => [r.rung.rung, r.kind, r.base, r.size, r.change])).toEqual([
      ["risk_premium", "total", 0, 50000, null],
      ["expense_loading", "increase", 50000, 5000, 5000],
      ["constraints", "decrease", 54000, 1000, -1000],
      ["payable_premium", "total", 0, 54000, 0],
    ]);
  });

  it("states each recorded operation with its operands exactly as sent", () => {
    expect(describeOperation(RUNGS[1]!.operation)).toBe("× 1.1");
    expect(describeOperation(RUNGS[2]!.operation)).toBe("clamp to max 54000");
    expect(describeOperation(RUNGS[3]!.operation)).toBe("round half_even to 0 dp");
    expect(describeOperation(undefined)).toBe("");
  });

  it("OQ-551: formats minor units as two-decimal major units with no currency symbol", () => {
    expect(formatAmount(123456)).toMatch(/^1.234.56$/);
    expect(formatAmount(5)).toMatch(/^0.05$/);
    expect(formatAmount(-1000)).not.toMatch(/[£€$]/);
  });
});
