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
    // A JS number is a float64. `0.1 + 0.2` is the reason this is a string (FR-OVR-7);
    // never `parseFloat` it — display it, or compute with a decimal library.
    expectTypeOf<OneWayRow["exposure_years"]>().toEqualTypeOf<string>();
  });

  it("keeps an exact amount as an integer count of minor units", () => {
    expectTypeOf<OneWayRow["claim_amount_minor"]>().toEqualTypeOf<number>();
  });

  it("marks the two ratios that merely look like money", () => {
    // `severity_minor` and `burning_cost_minor` end in `_minor` and are **floats**: they
    // are statistics (amount ÷ claims, amount ÷ exposure), not amounts. Formatting all
    // three `_minor` fields identically as currency is the mistake this guards.
    expectTypeOf<OneWayRow["severity_minor"]>().toEqualTypeOf<number | null | undefined>();
    expectTypeOf<OneWayRow["burning_cost_minor"]>().toEqualTypeOf<number | null | undefined>();
  });

  it("names the fields whose suffix does not mean an exact amount", () => {
    const ratios = ["severity_minor", "burning_cost_minor"] as const;
    const exact = ["claim_amount_minor"] as const;
    expect(new Set([...ratios, ...exact]).size).toBe(3);
  });
});
