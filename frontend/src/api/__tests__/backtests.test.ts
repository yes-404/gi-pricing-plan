import { describe, expect, it } from "vitest";

import { periodLabel } from "@/api/backtests";
import type { BacktestSummary } from "@/api/backtests";

// Only the two fields `periodLabel` reads. Annotated and cast at the call rather than
// `as BacktestSummary` inline, so a required field added to the contract does not silently
// pass here — the cast is in one place and says exactly what it hides.
// (`comparisons.test.ts:9-12`'s `jobWith` is the precedent for this shape.)
function summaryWith(period: Partial<BacktestSummary>): BacktestSummary {
  return period as BacktestSummary;
}

describe("periodLabel", () => {
  // FR-MODEL-57 calls a backtest "the evidence bridge into 05-monitoring.md", and
  // `backtests.py` adds that "a deterioration nobody can date is not evidence of drift".
  // So the window is shown whenever the artifact carries one.
  it("reads a closed window as a range", () => {
    expect(periodLabel(summaryWith({ period_from: "2025-01-01", period_to: "2025-12-31" })))
      .toBe("2025-01-01 to 2025-12-31");
  });

  // Both fields are optional AND nullable, so absence has two representations and the view
  // must not print an empty date for either. Null is the wire form; undefined is what an
  // omitted key deserialises to.
  it("returns null when the artifact declares no window at all", () => {
    expect(periodLabel(summaryWith({ period_from: null, period_to: null }))).toBeNull();
    expect(periodLabel(summaryWith({}))).toBeNull();
  });

  // A half-open window is representable: `backtests.py`'s validator only orders the pair
  // when both are present, so one-sided is a state the artifact can reach.
  it("names which end it has when only one is declared", () => {
    expect(periodLabel(summaryWith({ period_from: "2025-01-01", period_to: null })))
      .toBe("from 2025-01-01");
    expect(periodLabel(summaryWith({ period_from: null, period_to: "2025-12-31" })))
      .toBe("to 2025-12-31");
  });
});
