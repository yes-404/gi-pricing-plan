import { describe, expect, it } from "vitest";

import { formatDecimalString, formatMinor } from "../versions";

describe("formatting an exact decimal without parsing it", () => {
  it("keeps every digit the backend computed", () => {
    // The value the platform stores for freMTPL2's full exposure. `parseFloat` would be
    // arithmetic on a number the backend already summed exactly (FR-10).
    expect(formatDecimalString("339006.500000")).toBe("339,006.5");
    expect(formatDecimalString("21.000000")).toBe("21");
  });

  it("does not round a value it cannot represent as a float", () => {
    // 0.1 + 0.2 in float64 is 0.30000000000000004. A string passes through untouched.
    expect(formatDecimalString("0.300000", 6)).toBe("0.3");
    expect(formatDecimalString("1234567.891234", 6)).toBe("1,234,567.891234");
  });

  it("handles negatives and whole numbers", () => {
    expect(formatDecimalString("-1234.500000")).toBe("-1,234.5");
    expect(formatDecimalString("7")).toBe("7");
  });
});

describe("formatting money from integer minor units", () => {
  it("divides for display only", () => {
    // £2,500.00 arrives as 250000 pence. The integer is what makes it exact; the division
    // happens at the last possible moment, for a human.
    expect(formatMinor(250_000, "GBP")).toMatch(/2,500\.00/);
    expect(formatMinor(1, "EUR")).toMatch(/0\.01/);
  });

  it("uses the dataset's currency, not a hard-coded one", () => {
    // freMTPL2 is a French book: EUR. A platform that assumed GBP would mislabel every
    // figure on the screen while getting the arithmetic right.
    expect(formatMinor(407_540_056, "EUR")).not.toEqual(formatMinor(407_540_056, "GBP"));
  });
});
