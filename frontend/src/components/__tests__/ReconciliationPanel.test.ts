import { render } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import type { components } from "@/api/generated/schema";
import ReconciliationPanel from "../ReconciliationPanel.vue";

type Reconciliation = components["schemas"]["Reconciliation"];

// Every required field of `Reconciliation`, read from the generated contract. `ratio` and
// `tolerance` are `DecimalStr` — strings on the wire, never floats.
const RECONCILIATION = {
  dataset_version_id: "11111111-1111-1111-1111-111111111111",
  part: "holdout",
  perils: [
    { peril: "AD", large_loss_kind: "capped", modelled_burning_cost_minor: 7500 },
    { peril: "TP_BI", large_loss_kind: "separate_model", modelled_burning_cost_minor: 2500 },
  ],
  observed_burning_cost_minor: 10200,
  modelled_burning_cost_minor: 10000,
  tolerance: "0.05",
  computed_at: "2026-08-25T00:00:00Z",
  ratio: "0.9804",
  status: "pass",
} as unknown as Reconciliation;

function panel(reconciliation: Reconciliation = RECONCILIATION): string {
  const { container } = render(ReconciliationPanel, { props: { reconciliation } });
  return container.textContent ?? "";
}

describe("ReconciliationPanel", () => {
  it("shows FR-MODEL-60's verdict as it arrived, not as recomputed", () => {
    // `ratio` and `status` are `computed_field`s: derived server-side and discarded by the
    // model's own validator on the way in. Rendering a second, client-side computation is the
    // "two statements of one fact disagree eventually" defect.
    const text = panel();
    expect(text).toContain("pass");
    expect(text).toContain("0.9804");
    expect(text).toContain("0.05");
  });

  it("says which part the verdict is over (FR-MODEL-60's holdout)", () => {
    expect(panel()).toContain("holdout");
  });

  it("states each peril's treatment beside its share (FR-MODEL-74)", () => {
    const text = panel();
    expect(text).toContain("TP_BI");
    expect(text).toContain("separate_model");
    expect(text).toContain("75");
  });

  it("prints no currency symbol and no raw minor amount", () => {
    // The test that keeps Finding 3 honest. Without it a later change threading a `currency`
    // default in would pass every other assertion — and "GBP" over a euro-denominated
    // structure is invisible precisely because it looks right.
    const text = panel();
    expect(text).not.toMatch(/[£$€]/);
    expect(text).not.toContain("10000");
    expect(text).not.toContain("10200");
    expect(text).not.toContain("minor units");
  });

  it("renders a peril code as it arrives, never slugified", () => {
    // `PerilCode` is UPPER_SNAKE. `TP_BI` is the identifier a user recognises from their own
    // data, and lowercasing it makes it unmatchable against every other surface.
    expect(panel()).toContain("TP_BI");
    expect(panel()).not.toContain("tp-bi");
  });

  it("does not divide by a zero modelled total", () => {
    // A structure modelling nothing has no shares — a different statement from "0%".
    const empty = {
      ...RECONCILIATION,
      modelled_burning_cost_minor: 0,
      perils: [{ peril: "AD", large_loss_kind: "capped", modelled_burning_cost_minor: 0 }],
    } as unknown as Reconciliation;
    const text = panel(empty);
    expect(text).not.toContain("NaN");
    expect(text).not.toContain("Infinity");
  });
});
