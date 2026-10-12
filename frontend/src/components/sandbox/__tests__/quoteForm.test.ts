import { describe, expect, it } from "vitest";

import { buildInputs, type ContractField } from "../quoteForm";

const FIELDS: ContractField[] = [
  { name: "driver_age", type: "int", nullable: false, min: 17, max: 99 },
  { name: "ncd_discount", type: "decimal", nullable: false },
  { name: "channel", type: "enum", nullable: false, domain: ["direct", "broker"] },
  { name: "postcode", type: "string", nullable: true },
  { name: "is_telematics", type: "bool", nullable: false },
  { name: "start", type: "date", nullable: false },
];

const RAW = {
  driver_age: "34",
  ncd_discount: "0.35",
  channel: "direct",
  postcode: "",
  is_telematics: true,
  start: "2026-10-12",
};

describe("building a quote's inputs from the input contract (FR-213)", () => {
  it("types each field by its declared type", () => {
    const built = buildInputs(FIELDS, RAW);
    expect(built.problems).toEqual({});
    expect(built.inputs).toEqual({
      driver_age: 34,
      ncd_discount: 0.35,
      channel: "direct",
      postcode: null,
      is_telematics: true,
      start: "2026-10-12",
    });
  });

  it("refuses a non-integer where an int is declared, and says which field", () => {
    expect(buildInputs(FIELDS, { ...RAW, driver_age: "34.5" }).problems).toEqual({
      driver_age: "Enter a whole number",
    });
  });

  it("refuses a non-number where a decimal is declared", () => {
    expect(buildInputs(FIELDS, { ...RAW, ncd_discount: "abc" }).problems).toEqual({
      ncd_discount: "Enter a number",
    });
  });

  it("requires a non-nullable field and sends null for a blank nullable one", () => {
    const built = buildInputs(FIELDS, { ...RAW, channel: "", postcode: "  " });
    expect(built.problems).toEqual({ channel: "Required" });
    expect(built.inputs["postcode"]).toBeNull();
  });

  it("reads an unchecked box as false, never as missing", () => {
    expect(buildInputs(FIELDS, { ...RAW, is_telematics: undefined }).inputs["is_telematics"]).toBe(false);
  });

  it("does not re-check range or domain: the platform's contract check owns them", () => {
    // 17..99 is declared, 5 is out of range, and the client still sends it.
    const built = buildInputs(FIELDS, { ...RAW, driver_age: "5", channel: "elsewhere" });
    expect(built.problems).toEqual({});
    expect(built.inputs["driver_age"]).toBe(5);
    expect(built.inputs["channel"]).toBe("elsewhere");
  });
});
