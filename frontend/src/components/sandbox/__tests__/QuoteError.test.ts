import { render, screen } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import { ProblemError } from "@/api/problem";

import QuoteError from "../QuoteError.vue";

function problem(code: string, detail: string): ProblemError {
  return new ProblemError({
    type: "about:blank",
    title: "Unprocessable",
    status: 422,
    code,
    detail,
    errors: code === "INPUT_CONTRACT_VIOLATION" ? [{ field: "driver_age", code: "range", message: "below minimum" }] : [],
    trace_id: "abc123",
  });
}

describe("QuoteError (FR-255)", () => {
  it.each([
    ["INPUT_CONTRACT_VIOLATION", "Contract violation"],
    ["REFERENCE_LOOKUP_MISS", "Reference miss"],
    ["RATE_TABLE_MISS", "Table miss"],
    ["MODEL_CALL_FAILED", "Model failure"],
  ])("%s is its own heading, %s", (code, heading) => {
    render(QuoteError, { props: { error: problem(code, "the detail") } });
    expect(screen.getByRole("alert")).toHaveTextContent(heading);
    expect(screen.getByRole("alert")).toHaveTextContent(code);
    expect(screen.getByRole("alert")).toHaveTextContent("the detail");
  });

  it("names the field a contract violation concerns, and the trace id", () => {
    render(QuoteError, { props: { error: problem("INPUT_CONTRACT_VIOLATION", "bad") } });
    expect(screen.getByRole("alert")).toHaveTextContent("driver_age: below minimum");
    expect(screen.getByRole("alert")).toHaveTextContent("trace abc123");
  });

  it("shows any other code under its own title and code, never a generic failure", () => {
    render(QuoteError, { props: { error: problem("LADDER_RECONCILIATION_FAILED", "rung off by 1") } });
    expect(screen.getByRole("alert")).toHaveTextContent("Unprocessable");
    expect(screen.getByRole("alert")).toHaveTextContent("LADDER_RECONCILIATION_FAILED");
  });
});
