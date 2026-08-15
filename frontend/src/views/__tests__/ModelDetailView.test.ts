import { render, screen, within } from "@testing-library/vue";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import ModelDetailView from "../ModelDetailView.vue";

const MODEL = {
  id: "11111111-1111-4111-8111-111111111111",
  model_family_slug: "motor-frequency",
  version: 2,
  status: "fitted",
  spec_hash: "sha256:abc",
  dataset_version_id: "22222222-2222-4222-8222-222222222222",
  spec: {
    model_type: "glm", model_family_slug: "motor-frequency",
    dataset_version_id: "22222222-2222-4222-8222-222222222222",
    response_column: "claim_count", family: "poisson", link: "log",
    offset: { kind: "log_column", column: "exposure_years" },
    weight: { kind: "none" }, factors: [], family_params: {},
    alpha: 0, l1_ratio: 0, max_iter: 200, tolerance: 1e-8, seed: 0, peril: null,
  },
  fit_result: {
    model_type: "glm", converged: true, iterations: 6, fit_seconds: 0.42, rows: 400,
    coefficients: [
      { term: "intercept", estimate: -2.4181, std_error: 0.0121, z: -199.8, p_value: 0,
        ci_95: [-2.4418, -2.3944], relativity: 0.089 },
      { term: "area[urban]", estimate: 0.6931, std_error: 0.0184, z: 37.7, p_value: 0,
        ci_95: [0.6571, 0.7291], relativity: 2.0 },
      { term: "noise", estimate: 0.0100, std_error: 0.0400, z: 0.25, p_value: 0.80,
        ci_95: [-0.0684, 0.0884], relativity: 1.01 },
    ],
    relativities: {
      area: [
        { level: "rural", relativity: 1.0, is_base: true, exposure: 200.0 },
        { level: "urban", relativity: 2.0, is_base: false, exposure: 200.0 },
      ],
    },
    library_versions: { glum: "3.4.1", polars: "1.35.0" },
    dispersion: null, deviance: null,
  },
  parent_model_id: null, change_reason: null, flags: [],
};

function stub(body: unknown = MODEL, status = 200): void {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () =>
      new Response(JSON.stringify(body), {
        status, headers: { "Content-Type": "application/json" },
      }),
    ),
  );
}

beforeEach(() => stub());
afterEach(() => vi.unstubAllGlobals());

const props = { slug: "motor-frequency" };
const mounted = { global: { stubs: { RouterLink: { template: "<a><slot /></a>" } } } };

describe("the model detail view", () => {
  it("shows every estimate with its interval, never a bare point estimate", async () => {
    // `02` R5: uncertainty is part of what an estimate *is*. A column of point estimates
    // invites the reading it exists to prevent.
    render(ModelDetailView, { props, ...mounted });
    const table = await screen.findByRole("table", { name: "Coefficients" });

    const urban = within(table).getByText("area[urban]").closest("tr")!;
    expect(urban).toHaveTextContent("0.6931");
    expect(urban).toHaveTextContent("0.0184");
    expect(urban).toHaveTextContent("0.657");
    expect(urban).toHaveTextContent("0.729");
  });

  it("marks a coefficient whose interval spans zero", async () => {
    // Not distinguished from no effect at all — the one thing a reader must not miss in a
    // table where every other row looks equally definite.
    render(ModelDetailView, { props, ...mounted });
    const table = await screen.findByRole("table", { name: "Coefficients" });

    const noise = within(table).getByText("noise").closest("tr")!;
    expect(within(noise).getByText("spans zero")).toBeInTheDocument();
    const urban = within(table).getByText("area[urban]").closest("tr")!;
    expect(within(urban).queryByText("spans zero")).toBeNull();
  });

  it("shows the base level of a relativity table, at 1.000 and marked", async () => {
    // FR-MODEL-21. Omitting it is how a reader ends up believing a factor has one fewer
    // level than it has.
    render(ModelDetailView, { props, ...mounted });
    const table = await screen.findByRole("table", { name: "area relativities" });

    const rural = within(table).getByText("rural").closest("tr")!;
    expect(within(rural).getByText("base")).toBeInTheDocument();
    expect(rural).toHaveTextContent("1.000");
    expect(within(table).getAllByRole("row")).toHaveLength(3); // header + two levels
  });

  it("says a reserved model is not yet fitted rather than showing an empty table", async () => {
    stub({ ...MODEL, status: "draft", fit_result: null });
    render(ModelDetailView, { props, ...mounted });
    expect(await screen.findByText(/not yet fitted/)).toBeInTheDocument();
    expect(screen.queryByRole("table", { name: "Coefficients" })).toBeNull();
  });

  it("names the libraries the fit used", async () => {
    // A coefficient is only reproducible against the version that produced it.
    render(ModelDetailView, { props, ...mounted });
    expect(await screen.findByText(/glum 3.4.1, polars 1.35.0/)).toBeInTheDocument();
  });
});
