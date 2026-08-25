import { render, screen } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import CheckStatusBadge from "../CheckStatusBadge.vue";

// `@testing-library/vue`, not `@vue/test-utils` — the latter is not a dependency here.
type CheckStatus = "pass" | "warn" | "violated" | "failed";

function badge(status: CheckStatus): HTMLElement {
  const { container } = render(CheckStatusBadge, { props: { status } });
  return container.firstElementChild as HTMLElement;
}

describe("CheckStatusBadge", () => {
  // FR-MODEL-43, as amended 2026-08-25: a view rendering a certificate must not style, label,
  // group or order a `violated` check as a failure. This is the label half.
  it("labels violated as a finding, not a failure", () => {
    const text = (badge("violated").textContent ?? "").toLowerCase();
    expect(text).toContain("finding");
    expect(text).not.toContain("fail");
  });

  // And the style half. Asserted as "differs from failed's" rather than against a literal
  // class string, so a palette change cannot silently satisfy it.
  it("gives violated and failed different tones", () => {
    expect(badge("violated").className).not.toBe(badge("failed").className);
  });

  // The other direction of the same rule: `violated` must read like the other non-blocking
  // finding, not like the blocking one. Without this, tinting `violated` its own third colour
  // passes the test above while still setting it apart from an ordinary finding.
  it("gives violated the same tone as warn, the other non-blocking finding", () => {
    expect(badge("violated").className).toBe(badge("warn").className);
  });

  it("carries the status in text, not by colour alone", () => {
    for (const status of ["pass", "warn", "violated", "failed"] as const) {
      expect((badge(status).textContent ?? "").trim()).not.toBe("");
    }
  });

  it("still calls a genuine failure a failure", () => {
    // The control. A badge that never says "failed" would pass the violated assertions above
    // for the wrong reason.
    expect((badge("failed").textContent ?? "").toLowerCase()).toContain("failed");
    expect(screen.queryAllByText("failed").length).toBeGreaterThan(0);
  });
});
