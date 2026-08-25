import { render, screen, waitFor, within } from "@testing-library/vue";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import FactorWorkbenchView from "../FactorWorkbenchView.vue";

/**
 * The factor workbench (`02` §5.3).
 *
 * The claim under test is the **interaction requirement**: an edit's consequence is
 * visible before it is saved. So the tests assert on what reaches the wire — that moving a
 * boundary calls `/bandings/evaluate` and that re-pointing a level calls
 * `/groupings/evaluate` — and that an edit which cannot be valid is refused *without* a
 * request, because a 422 per keystroke is not an editor.
 *
 * `fetch` is stubbed per-route rather than globally, so a view that called the wrong
 * endpoint fails rather than quietly receiving the one fixture.
 */

const VERSION_ID = "33333333-3333-4333-8333-333333333333";
const DATASET_ID = "44444444-4444-4444-8444-444444444444";

const VERSION = { id: VERSION_ID, dataset_id: DATASET_ID, version: 3, status: "validated" };

const PROFILE = {
  id: "55555555-5555-4555-8555-555555555555",
  dataset_version_id: VERSION_ID,
  row_count: 1000,
  columns: [],
  one_ways: [
    { column: "driver_age", banding: "levels", rows: [] },
    { column: "region", banding: "levels", rows: [] },
  ],
  library_versions: {},
};

function band(level: string, exposure: string, claims: number, frequency: number) {
  return {
    level,
    exposure_years: exposure,
    claim_count: claims,
    claim_amount_minor: claims * 100_000,
    frequency,
    frequency_ci: [frequency * 0.9, frequency * 1.1],
    mean_severity: 100_000,
    severity_ci: null,
    mean_burning_cost: frequency * 100_000,
  };
}

const BANDING = {
  id: "66666666-6666-4666-8666-666666666666",
  slug: "driver-age-3",
  dataset_id: DATASET_ID,
  version: 1,
  column: "driver_age",
  method: "exposure_quantile",
  method_params: { n_bands: 3 },
  derived_on_dataset_version_id: VERSION_ID,
  boundaries: [18, 30, 50, 80],
  closed: "left",
  labels: ["18-29", "30-49", "50+"],
  null_level: null,
  below_range: "error",
  above_range: "error",
  band_stats: [
    band("18-29", "100.0", 40, 0.4),
    band("30-49", "200.0", 50, 0.25),
    // Deliberately thin: the view shades a band under thirty claims.
    band("50+", "300.0", 12, 0.04),
  ],
};

const GROUPING = {
  id: "77777777-7777-4777-8777-777777777777",
  slug: "region-2",
  dataset_id: DATASET_ID,
  version: 1,
  column: "region",
  method: "hierarchical_clustering",
  method_params: {},
  credibility_standard: null,
  derived_on_dataset_version_id: VERSION_ID,
  mapping: { N1: "G1", N2: "G1", S1: "G2" },
  unseen_level_behaviour: "map_to_default",
  default_target_level: "G1",
  parent_grouping_id: null,
  evidence: {
    source_level_count: 3,
    target_level_count: 2,
    deviance_before: 1000.0,
    deviance_after: 1001.2,
    df_saved: 1,
    chi2_p_value: 0.27,
    target_level_stats: [],
  },
};

/** Every request the view makes, in order — the record the assertions read. */
let calls: { url: string; body: unknown }[] = [];
let overrides: Record<string, unknown> = {};

function routeFor(url: string): unknown {
  for (const [fragment, body] of Object.entries(overrides)) {
    if (url.includes(fragment)) return body;
  }
  if (url.includes("/profile")) return PROFILE;
  if (url.includes("/bandings/propose") || url.includes("/bandings/evaluate")) return BANDING;
  if (url.includes("/bandings")) return { ...BANDING, version: 2 };
  if (url.includes("/groupings/propose") || url.includes("/groupings/evaluate")) return GROUPING;
  if (url.includes("/groupings")) return { ...GROUPING, version: 2 };
  if (url.includes("/dataset-versions/")) return VERSION;
  // The model selector added by W6b-5b: the panel's candidates are a per-Model artifact
  // reached from a Dataset-Version-scoped view (OQ-MODEL-40). Empty here — this file tests
  // the banding and grouping editors, and the selector has its own suite.
  if (url.includes("/models")) return { items: [], next_cursor: null, total_estimate: 0 };
  throw new Error(`the view asked for an endpoint the test does not stub: ${url}`);
}

beforeEach(() => {
  calls = [];
  overrides = {};
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: URL | string, init?: RequestInit) => {
      const url = String(input);
      calls.push({ url, body: init?.body ? JSON.parse(String(init.body)) : undefined });
      return new Response(JSON.stringify(routeFor(url)), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    }),
  );
});

afterEach(() => vi.unstubAllGlobals());

const mounted = { global: { stubs: { RouterLink: { template: "<a><slot /></a>" } } } };
const props = { datasetVersionId: VERSION_ID };

function evaluateCalls(kind: "bandings" | "groupings") {
  return calls.filter((c) => c.url.includes(`/${kind}/evaluate`));
}

describe("the factor workbench", () => {
  it("resolves its dataset version by id, which is all the route gives it", async () => {
    render(FactorWorkbenchView, { props, ...mounted });
    await waitFor(() => expect(screen.getByLabelText("Column to band")).toBeTruthy());
    expect(calls.some((c) => c.url.includes(`/dataset-versions/${VERSION_ID}`))).toBe(true);
  });

  it("offers the profile's candidate rating columns and nothing else", async () => {
    render(FactorWorkbenchView, { props, ...mounted });
    const select = (await screen.findByLabelText("Column to band")) as HTMLSelectElement;
    expect([...select.options].map((o) => o.value)).toEqual(["driver_age", "region"]);
  });

  it("shows each band's statistics with the interval, not just the frequency", async () => {
    const user = userEvent.setup();
    render(FactorWorkbenchView, { props, ...mounted });
    await user.click(await screen.findByRole("button", { name: "Propose" }));

    const row = (await screen.findByText("18-29")).closest("tr")!;
    expect(within(row).getByText("0.4000")).toBeTruthy();
    // `02` R5: the interval is what says whether the estimate is worth reading.
    expect(within(row).getByText("0.3600 – 0.4400")).toBeTruthy();
  });

  it("marks a band too thin to estimate from", async () => {
    const user = userEvent.setup();
    render(FactorWorkbenchView, { props, ...mounted });
    await user.click(await screen.findByRole("button", { name: "Propose" }));

    const thin = (await screen.findByText("50+")).closest("tr")!;
    expect(thin.className).toContain("amber");
    const healthy = screen.getByText("30-49").closest("tr")!;
    expect(healthy.className).not.toContain("amber");
  });

  it("re-evaluates against the platform when a boundary moves (FR-MODEL-83)", async () => {
    const user = userEvent.setup();
    render(FactorWorkbenchView, { props, ...mounted });
    await user.click(await screen.findByRole("button", { name: "Propose" }));
    expect(evaluateCalls("bandings")).toHaveLength(0);

    const cut = await screen.findByLabelText("Boundary 1");
    await user.clear(cut);
    await user.type(cut, "35");
    await user.tab();

    await waitFor(() => expect(evaluateCalls("bandings")).toHaveLength(1));
    const sent = evaluateCalls("bandings")[0]!.body as {
      dataset_version_id: string;
      banding: { boundaries: number[] };
    };
    expect(sent.dataset_version_id).toBe(VERSION_ID);
    expect(sent.banding.boundaries).toEqual([18, 35, 50, 80]);
  });

  it("refuses a boundary that would cross its neighbour, without asking the platform", async () => {
    const user = userEvent.setup();
    render(FactorWorkbenchView, { props, ...mounted });
    await user.click(await screen.findByRole("button", { name: "Propose" }));

    const cut = await screen.findByLabelText("Boundary 1");
    await user.clear(cut);
    await user.type(cut, "60"); // past boundary 2, which is 50
    await user.tab();

    await waitFor(() => expect(cut.getAttribute("aria-invalid")).toBe("true"));
    expect(evaluateCalls("bandings")).toHaveLength(0);
    // The last valid evaluation is still on screen — an invalid keystroke does not blank it.
    expect(screen.getByText("18-29")).toBeTruthy();
  });

  it("cannot move the outer boundaries, which define the banded range", async () => {
    const user = userEvent.setup();
    render(FactorWorkbenchView, { props, ...mounted });
    await user.click(await screen.findByRole("button", { name: "Propose" }));

    expect((await screen.findByLabelText("Boundary 0")).hasAttribute("disabled")).toBe(true);
    expect(screen.getByLabelText("Boundary 3").hasAttribute("disabled")).toBe(true);
  });

  it("saves the edited banding against the dataset the version belongs to", async () => {
    const user = userEvent.setup();
    render(FactorWorkbenchView, { props, ...mounted });
    await user.click(await screen.findByRole("button", { name: "Propose" }));
    await user.click(await screen.findByRole("button", { name: "Save banding" }));

    await waitFor(() => expect(screen.getByText(/version 2/)).toBeTruthy());
    const saved = calls.find(
      (c) => c.url.endsWith("/bandings") && c.body !== undefined,
    )!.body as { dataset_id: string };
    // The route carries a *version* id; a Banding is keyed to the **dataset**.
    expect(saved.dataset_id).toBe(DATASET_ID);
  });

  it("shows the deviance and df a merge costs, and reads the p-value out loud", async () => {
    const user = userEvent.setup();
    render(FactorWorkbenchView, { props, ...mounted });
    await user.click(await screen.findByRole("tab", { name: "grouping" }));
    await user.click(await screen.findByRole("button", { name: "Propose" }));

    const verdict = await screen.findByTestId("merge-verdict");
    expect(verdict.textContent).toContain("3 levels → 2");
    expect(verdict.textContent).toContain("1 degrees of freedom saved");
    expect(verdict.textContent).toContain("does not distinguish");
    expect(verdict.textContent).toContain("1000.0");
    expect(verdict.textContent).toContain("1001.2");
  });

  it("says so when a merge discards real signal", async () => {
    overrides = {
      "/groupings/propose": {
        ...GROUPING,
        evidence: { ...GROUPING.evidence, chi2_p_value: 1e-9 },
      },
    };
    const user = userEvent.setup();
    render(FactorWorkbenchView, { props, ...mounted });
    await user.click(await screen.findByRole("tab", { name: "grouping" }));
    await user.click(await screen.findByRole("button", { name: "Propose" }));

    const verdict = await screen.findByTestId("merge-verdict");
    expect(verdict.textContent).toContain("discards real signal");
    expect(verdict.className).toContain("red");
  });

  it("re-evaluates the evidence when a level is pointed elsewhere (FR-MODEL-83)", async () => {
    const user = userEvent.setup();
    render(FactorWorkbenchView, { props, ...mounted });
    await user.click(await screen.findByRole("tab", { name: "grouping" }));
    await user.click(await screen.findByRole("button", { name: "Propose" }));
    expect(evaluateCalls("groupings")).toHaveLength(0);

    await user.selectOptions(await screen.findByLabelText("Target for S1"), "G1");

    await waitFor(() => expect(evaluateCalls("groupings")).toHaveLength(1));
    const sent = evaluateCalls("groupings")[0]!.body as {
      grouping: { mapping: Record<string, string> };
    };
    expect(sent.grouping.mapping).toEqual({ N1: "G1", N2: "G1", S1: "G1" });
  });

  it("surfaces a refusal as the problem the platform sent", async () => {
    render(FactorWorkbenchView, { props, ...mounted });
    await screen.findByLabelText("Column to band");

    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        new Response(
          JSON.stringify({
            type: "about:blank",
            title: "Dataset version is not validated",
            status: 409,
            code: "DATASET_NOT_VALIDATED",
            detail: "This version has status 'draft'; fitting requires 'validated'.",
          }),
          { status: 409, headers: { "Content-Type": "application/problem+json" } },
        ),
      ),
    );

    await userEvent.setup().click(screen.getByRole("button", { name: "Propose" }));
    expect(await screen.findByText(/requires 'validated'/)).toBeTruthy();
  });
});
