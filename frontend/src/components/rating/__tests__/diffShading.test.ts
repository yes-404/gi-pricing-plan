import { describe, expect, it } from "vitest";

import { shadeChange } from "../diffShading";

describe("shadeChange (FR-231)", () => {
  it("gives a cell with no relative change no shade and no direction", () => {
    expect(shadeChange(null)).toEqual({ direction: "none", step: 0, label: "—" });
    expect(shadeChange("0")).toEqual({ direction: "none", step: 0, label: "0%" });
  });

  it("names the direction in words as well as in the shade, so colour is never the only channel", () => {
    expect(shadeChange("3.5")).toMatchObject({ direction: "up", label: "+3.5%" });
    expect(shadeChange("-3.5")).toMatchObject({ direction: "down", label: "-3.5%" });
  });

  it("steps the shade up with the size of the change, the same for a rise and a fall", () => {
    const steps = ["0.4", "2", "7", "15", "40"].map((rel) => shadeChange(rel).step);
    expect(steps).toEqual([1, 2, 3, 4, 4]);
    expect(shadeChange("-7").step).toBe(shadeChange("7").step);
  });

  it("keeps a decimal string beyond double precision exactly as written in its label", () => {
    expect(shadeChange("1.050000000000000001").label).toBe("+1.050000000000000001%");
  });
});
