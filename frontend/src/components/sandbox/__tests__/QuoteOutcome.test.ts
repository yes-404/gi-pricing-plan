import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import type { ScoringResult } from "@/api/score";

import QuoteOutcome from "../QuoteOutcome.vue";

const BASE: ScoringResult = {
  outcome: "quoted",
  rating_version_ref: "rating_version:motor-gb@1",
  bundle_hash: `sha256:${"a".repeat(64)}`,
  premium_ladder: [],
  outputs: { payable_premium_minor: 63000 },
};

describe("QuoteOutcome", () => {
  it("shows a quoted outcome and the declared outputs", () => {
    render(QuoteOutcome, { props: { result: BASE } });
    expect(screen.getByTestId("outcome")).toHaveTextContent("quoted");
    expect(screen.getByLabelText("Outputs")).toHaveTextContent("63000");
    expect(screen.queryByText(/declined —/i)).not.toBeInTheDocument();
  });

  it("FR-256: renders a decline as a result, with every reason listed", () => {
    render(QuoteOutcome, {
      props: { result: { ...BASE, outcome: "declined", decline_reasons: ["AGE_BELOW_MIN", "BAD_POSTCODE"] } },
    });
    expect(screen.getByTestId("outcome")).toHaveTextContent("declined");
    const reasons = within(screen.getByLabelText("Decline reasons")).getAllByRole("listitem");
    expect(reasons.map((li) => li.textContent?.trim())).toEqual(["AGE_BELOW_MIN", "BAD_POSTCODE"]);
  });

  it("FR-249 (R6.1, OQ-1460): says per-peril components are absent, whatever the result holds", () => {
    render(QuoteOutcome, { props: { result: BASE } });
    expect(screen.getByTestId("per-peril-absent")).toHaveTextContent(/not available/i);
    expect(screen.getByTestId("per-peril-absent")).toHaveTextContent("OQ-1460");
  });
});
