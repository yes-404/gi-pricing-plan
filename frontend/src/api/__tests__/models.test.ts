import { describe, expect, it } from "vitest";

import { intervalWidth, relativityInterval, spansZero, type Coefficient } from "../models";

function coefficient(over: Partial<Coefficient> = {}): Coefficient {
  return {
    term: "t", estimate: 0.5, std_error: 0.1, z: 5, p_value: 0,
    ci_95: [0.3, 0.7], relativity: 1.65, ...over,
  } as Coefficient;
}

describe("reading a coefficient", () => {
  it("measures an interval's width", () => {
    expect(intervalWidth(coefficient())).toBeCloseTo(0.4, 10);
  });

  it("knows an interval that spans zero from one that does not", () => {
    // The distinction the screen marks: not distinguished from no effect at all.
    expect(spansZero(coefficient({ ci_95: [-0.1, 0.9] }))).toBe(true);
    expect(spansZero(coefficient({ ci_95: [0.3, 0.7] }))).toBe(false);
    // A boundary case: an interval touching zero has not excluded it.
    expect(spansZero(coefficient({ ci_95: [0, 0.9] }))).toBe(true);
  });

  it("exponentiates the interval for a log link, because that is what the table shows", () => {
    // A relativity's interval is not the coefficient's interval — reading one as the other
    // understates the spread of every relativity above 1.
    const [low, high] = relativityInterval(coefficient({ ci_95: [0, Math.LN2] }));
    expect(low).toBeCloseTo(1.0, 10);
    expect(high).toBeCloseTo(2.0, 10);
  });
});
