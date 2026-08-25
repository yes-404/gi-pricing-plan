import { describe, expectTypeOf, it } from "vitest";

import type { PartitionCaption, PartitionLabel } from "@/api/diagnostics";
import { partitions } from "@/api/diagnostics";

/**
 * What `partitions()` actually produces as a caption.
 *
 * `NonNullable` rather than a bare `[number]` index because `tsconfig.app.json` sets
 * `noUncheckedIndexedAccess`, so indexing an array type yields `T | undefined` and `[0]` on
 * that union is a compile error rather than the tuple's first member. The helper is also
 * synchronous, so there is no promise to await.
 */
type ProducedCaption = NonNullable<ReturnType<typeof partitions>[number]>[0];

describe("PartitionCaption widens the presentation seam without widening the fit", () => {
  // FR-MODEL-57: a backtest's single partition is neither of the fit's two, and calling it
  // a holdout "would claim a split nobody made". The instruments must accept a third
  // caption; the fit's own vocabulary must not gain one.
  it("admits every fit label, so no existing caller has to change", () => {
    expectTypeOf<PartitionLabel>().toExtend<PartitionCaption>();
  });

  it("admits the backtest caption, which PartitionLabel does not", () => {
    expectTypeOf<"Backtest">().toExtend<PartitionCaption>();
    expectTypeOf<"Backtest">().not.toExtend<PartitionLabel>();
  });

  // The point of the supertype rather than widening in place. `partitions()` can only ever
  // produce Train and Holdout, so a return type advertising a third would be a false
  // statement about the function.
  //
  // **Asserted against the literal union, not against `PartitionLabel`.** The helper's
  // signature is written in terms of that alias, so comparing the two is a tautology: widen
  // `PartitionLabel` in place — the design this supertype exists to avoid — and both sides
  // move together and the assertion still passes. Proven by mutation: it took the literals
  // to make that mutation fail *this* test rather than only its neighbour.
  it("leaves partitions() producing exactly the fit's two", () => {
    expectTypeOf<ProducedCaption>().toEqualTypeOf<"Train" | "Holdout">();
  });

  // Closed, not `string`. A caption nobody specified is the defect FR-MODEL-57 guards.
  it("stays a closed union", () => {
    expectTypeOf<PartitionCaption>().not.toEqualTypeOf<string>();
    expectTypeOf<"Out-of-time">().not.toExtend<PartitionCaption>();
  });
});
