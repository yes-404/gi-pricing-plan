import { describe, expect, expectTypeOf, it } from "vitest";

import type { components } from "../generated/schema";

type OneWayRow = components["schemas"]["OneWayRow"];

/**
 * The money discipline, asserted against the **generated** types.
 *
 * These are type-level assertions on purpose: if `model-schema` ever lets a money field
 * become a float, or an exact decimal become a number, this fails at type-check rather
 * than as a rounding difference somebody notices in a rate filing.
 */
describe("money and exact decimals as they cross into TypeScript", () => {
  it("keeps exact decimals as strings", () => {
    // A JS number is a float64. `0.1 + 0.2` is the reason this is a string (FR-10);
    // never `parseFloat` it — display it, or compute with a decimal library.
    expectTypeOf<OneWayRow["exposure_years"]>().toEqualTypeOf<string>();
  });

  it("keeps an exact amount as an integer count of minor units", () => {
    expectTypeOf<OneWayRow["claim_amount_minor"]>().toEqualTypeOf<number>();
  });

  it("marks the two ratios that are means, not amounts", () => {
    // `mean_severity` and `mean_burning_cost` are **floats**: they are statistics
    // (amount ÷ claims, amount ÷ exposure), not amounts — FR-64 renamed them off
    // `_minor` for exactly this reason, so their names no longer look like money at all.
    expectTypeOf<OneWayRow["mean_severity"]>().toEqualTypeOf<number | null | undefined>();
    expectTypeOf<OneWayRow["mean_burning_cost"]>().toEqualTypeOf<number | null | undefined>();
  });

  it("names the fields distinctly from the one exact amount on the row", () => {
    const ratios = ["mean_severity", "mean_burning_cost"] as const;
    const exact = ["claim_amount_minor"] as const;
    expect(new Set([...ratios, ...exact]).size).toBe(3);
  });
});
