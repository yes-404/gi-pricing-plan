import { render, screen } from "@testing-library/vue";
import { afterEach, describe, expect, it, vi } from "vitest";

import * as api from "@/api/perils";
import PerilStructureDetailView from "../PerilStructureDetailView.vue";

/**
 * Shaped from the generated contract. **The model refs are strings**, not objects:
 * `ArtifactRef` overrides its JSON schema to emit `{"type": "string", "pattern": …}`, so the
 * wire carries the canonical `model:{slug}@{version}`. Writing the Python object's three
 * properties here would be a fixture the API never sends.
 */
const STRUCTURE = {
  id: "p1",
  slug: "motor-2026",
  version: 3,
  status: "reconciled",
  created_at: "2026-07-01T09:30:00Z",
  perils: [
    {
      peril: "AD",
      method: "frequency_severity",
      frequency_model: "model:ad-freq@4",
      severity_model: "model:ad-sev@2",
      large_loss: { kind: "capped", cap_minor: 500000, restoration_loading: "1.08" },
    },
    {
      peril: "TP_BI",
      method: "burning_cost",
      burning_cost_model: "model:tpbi-bc@1",
      large_loss: { kind: "flat_loading", loading_factor: "1.15" },
    },
  ],
  excluded_perils: [{ peril: "COURTESY_CAR", reason: "Bundled service cost" }],
  reconciliation: {
    dataset_version_id: "11111111-1111-1111-1111-111111111111",
    part: "holdout",
    perils: [{ peril: "AD", large_loss_kind: "capped", modelled_burning_cost: 10000 }],
    observed_burning_cost: 10200,
    modelled_burning_cost: 10000,
    tolerance: "0.05",
    computed_at: "2026-08-25T00:00:00Z",
    ratio: "0.9804",
    status: "pass",
  },
} as unknown as api.PerilStructure;

function detail(structure: api.PerilStructure = STRUCTURE) {
  vi.spyOn(api, "getPerilStructure").mockResolvedValue(structure);
  return render(PerilStructureDetailView, { props: { id: "p1" } });
}

afterEach(() => vi.restoreAllMocks());

describe("PerilStructureDetailView", () => {
  it("pins each model reference by version (FR-188)", async () => {
    // The canonical string, not its parts. Splitting it into "ad-freq (v4)" makes the pinned
    // reference unsearchable against traces and audit rows.
    const { container } = detail();
    expect(await screen.findByText("motor-2026 v3", { exact: false })).toBeInTheDocument();
    expect(container.textContent ?? "").toContain("model:ad-freq@4");
  });

  it("names every excluded peril and its reason (FR-190)", async () => {
    // The panel no noun in the §5.3 cell asked for, and which FR-190 requires: every
    // peril is either modelled or explicitly excluded with a reason.
    const { container } = detail();
    await screen.findByText("COURTESY_CAR:", { exact: false });
    expect(container.textContent ?? "").toContain("Bundled service cost");
  });

  it("renders a large-loss kind the platform cannot compute (Finding 5)", async () => {
    // `pricing_core` refuses `flat_loading` by name, but the contract carries all four kinds
    // and FR-207 makes that intended. A `v-if` over the computable pair would render a
    // blank treatment for a structure that declares one.
    const { container } = detail();
    await screen.findByText("Large-loss treatment");
    expect(container.textContent ?? "").toContain("flat_loading");
    expect(container.textContent ?? "").toContain("1.15");
  });

  it("states the treatment's parameters, not just its kind (FR-189)", async () => {
    // A panel saying `capped` without saying capped *at what* has not recorded the treatment,
    // only that there is one. Integer minor units, no symbol — the view cannot source a
    // currency (OQ-551) and will not assert one.
    const { container } = detail();
    await screen.findByText("Large-loss treatment");
    const text = container.textContent ?? "";
    expect(text).toContain("500000");
    expect(text).toContain("1.08");
    expect(text).not.toMatch(/[£$€]/);
  });

  it("names each peril's method, which decides what its refs mean (FR-188)", async () => {
    const { container } = detail();
    await screen.findByText("Composition");
    expect(container.textContent ?? "").toContain("frequency_severity");
    expect(container.textContent ?? "").toContain("burning_cost");
  });

  it("shows a draft structure as unreconciled rather than as an error", async () => {
    // Trap 3: the validator requires a reconciliation only in reconciled/review/approved, so
    // a draft having none is valid. Treating the null as a fetch failure shows an error over
    // a perfectly good structure.
    const draft = {
      ...STRUCTURE,
      status: "draft",
      reconciliation: null,
    } as unknown as api.PerilStructure;
    const { container } = detail(draft);

    await screen.findByText(/not yet reconciled/i);
    expect((container.textContent ?? "").toLowerCase()).not.toContain("error");
  });

  it("renders the reconciliation panel when the structure carries one", async () => {
    // The control for the test above: without it, "not yet reconciled" being absent from the
    // reconciled case would pass equally against a view that never renders the panel.
    const { container } = detail();
    await screen.findByText("Reconciliation");
    expect(container.textContent ?? "").toContain("0.9804");
    expect((container.textContent ?? "").toLowerCase()).not.toContain("not yet reconciled");
  });
});
