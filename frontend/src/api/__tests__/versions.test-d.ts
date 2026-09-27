import { describe, expectTypeOf, it } from "vitest";

import type { components } from "../generated/schema";

type VersionTotals = components["schemas"]["VersionTotals"];
type DatasetTable = components["schemas"]["DatasetTable"];

describe("the version's totals keep the money discipline", () => {
  it("carries exposure as an exact decimal string", () => {
    // 678 013 rows summed as float64 give 21.000000000000004 where Decimal gives 21.00.
    // The string is what stops the total disagreeing with the report that cites it.
    expectTypeOf<VersionTotals["exposure_years"]>().toEqualTypeOf<string>();
  });

  it("carries incurred as an integer count of minor units", () => {
    // Required, not optional: the model gives it a default of 0, so the contract always
    // carries a number. A reader never has to decide what an absent total means.
    expectTypeOf<VersionTotals["claim_amount_minor"]>().toEqualTypeOf<number>();
  });

  it("keeps the source header a column came from", () => {
    // FR-30. Normalisation is lossy — freMTPL2's `IDpol` becomes `i_dpol` — and
    // without this a user cannot tell which of their columns a rule is talking about.
    expectTypeOf<DatasetTable["source_names"]>().toEqualTypeOf<
      { [key: string]: string } | undefined
    >();
  });
});
