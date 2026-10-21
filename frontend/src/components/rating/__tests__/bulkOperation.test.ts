import { describe, expect, it } from "vitest";

import { buildBulkRequest, parseKeyLevels } from "../bulkOperation";

describe("parseKeyLevels (FR-233)", () => {
  it("reads one key column per line, its levels after the colon, comma separated", () => {
    expect(parseKeyLevels("area: A, B\nband: 17-20")).toEqual({ area: ["A", "B"], band: ["17-20"] });
  });

  it("ignores blank lines and trims, and keeps a level's own text", () => {
    expect(parseKeyLevels("\n  area :  A ,  B  \n\n")).toEqual({ area: ["A", "B"] });
  });

  it("refuses a line with no colon or no level, naming the line", () => {
    expect(() => parseKeyLevels("area A")).toThrow(/line 1/);
    expect(() => parseKeyLevels("area: A\nband:")).toThrow(/line 2/);
  });
});

describe("buildBulkRequest (FR-233)", () => {
  it("builds each kind's request with decimals exactly as typed", () => {
    expect(buildBulkRequest("uplift_table", { percentage: " 5.000000000000000001 " })).toEqual({
      kind: "uplift_table",
      parameters: { percentage: "5.000000000000000001" },
    });
    expect(buildBulkRequest("uplift_by_filter", { percentage: "-2", filter: "area: A" })).toEqual({
      kind: "uplift_by_filter",
      parameters: { percentage: "-2", filter: { area: ["A"] } },
    });
    expect(buildBulkRequest("floor_and_cap", { floor: "0.8", cap: "1.5" })).toEqual({
      kind: "floor_and_cap",
      parameters: { floor: "0.8", cap: "1.5" },
    });
    expect(buildBulkRequest("rebase_to_level", { base_level: "area: A" })).toEqual({
      kind: "rebase_to_level",
      parameters: { base_level: { area: ["A"] } },
    });
  });

  it("names the field a required value is missing from", () => {
    expect(() => buildBulkRequest("uplift_table", { percentage: " " })).toThrow(/percentage/);
    expect(() => buildBulkRequest("floor_and_cap", { floor: "1" })).toThrow(/cap/);
  });
});
