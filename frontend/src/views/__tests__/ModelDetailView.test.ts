import { render, screen, within } from "@testing-library/vue";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import ModelDetailView from "../ModelDetailView.vue";
import { ARTIFACT, boundOf, EBM_MODEL, GBM_MODEL } from "./fixtures";

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
        { level: "rural", relativity: 1.0, estimate: 0.0, is_base: true, exposure: 300.0 },
        { level: "urban", relativity: 2.0, estimate: 0.6931, is_base: false, exposure: 100.0 },
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

/**
 * A fetch stub that answers by URL, and 404s a transparency path it has no entry for.
 *
 * `stub()` above returns one body for every call, so it cannot express a page that fetches
 * twice: it would hand the Model back as the transparency artifact and the panel would
 * render whatever happened to match. The 404 body carries `code: "NOT_FOUND"` because the
 * view branches on the code and not on the status (`api/problem.ts`) — a stub that returned
 * a bare 404 would exercise a path the platform never produces.
 */
function stubByUrl(routes: Record<string, unknown>): ReturnType<typeof vi.fn> {
  const fetchMock = vi.fn(async (input: unknown) => {
    const url = String(input);
    const match = Object.keys(routes).find((path) => url.includes(path));
    if (match !== undefined) {
      return new Response(JSON.stringify(routes[match]), {
        status: 200, headers: { "Content-Type": "application/json" },
      });
    }
    const problem = {
      type: "about:blank", title: "Not found", status: 404, code: "NOT_FOUND",
      detail: `No route stubbed for ${url}`, errors: [],
    };
    return new Response(JSON.stringify(problem), {
      status: 404, headers: { "Content-Type": "application/json" },
    });
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
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

  it("shows the coefficient where a link has no relativity", async () => {
    // `exp(β)` is a reading of a multiplicative model. Under `logit` there is none, and
    // rendering 1.000 said "no effect" for a factor spanning eighteen log-odds.
    stub({
      ...MODEL,
      fit_result: {
        ...MODEL.fit_result,
        relativities: {
          area: [
            { level: "rural", relativity: null, estimate: 0.0, is_base: true, exposure: 300 },
            { level: "urban", relativity: null, estimate: 1.2, is_base: false, exposure: 100 },
          ],
        },
      },
    });
    render(ModelDetailView, { props, ...mounted });
    const table = await screen.findByRole("table", { name: "area relativities" });
    expect(within(table).getByText(/1.2000/)).toBeInTheDocument();
    expect(within(table).getAllByText(/on the link scale/).length).toBeGreaterThan(0);
    expect(within(table).queryByText("1.000")).toBeNull();
  });
});

describe("the model detail view, on a model that is not a GLM", () => {
  const gbmProps = { slug: "motor-ad-frequency" };

  it("does not call a fitted booster unfitted", async () => {
    // The empty state is about `fit_result`, not about the GLM narrowing. Read off the
    // narrowed ref it fires for every GBM and EBM ever fitted, and the page then states in
    // prose that a model which took forty seconds to fit was never fitted.
    stub(GBM_MODEL);
    render(ModelDetailView, { props: gbmProps, ...mounted });
    // `findAllByText`, not `findByText`: once the GBM panel mounts, `lightgbm` appears as the
    // header's backend, as `lightgbm_text`, and as a library version. Waiting on the singular
    // matcher would fail on the arm rendering *more*, which is the opposite of the point.
    expect((await screen.findAllByText(/lightgbm/i)).length).toBeGreaterThan(0);
    expect(screen.queryByText(/reserved but not yet fitted/i)).toBeNull();
  });

  it("renders the booster's features and constraints on the page", async () => {
    // Wait for the content, not the container: this view loads in one step but renders the
    // header before the panel exists, and asserting on the section would pass either way.
    stub(GBM_MODEL);
    render(ModelDetailView, { props: gbmProps, ...mounted });
    const table = await screen.findByRole("table", { name: "Features and constraints" });
    expect(within(table).getByText("driver_age_banded")).toBeInTheDocument();
  });

  it("says on the page itself that a bound is a bound, and links to what it bounds", async () => {
    // FR-MODEL-78. Nothing else on this page distinguishes a bound from the central estimate:
    // same family, same dataset version, same factors, same metadata block. The link text is
    // asserted rather than the anchor because `stubs: { RouterLink: true }` discards the slot,
    // and the assertion would then pass against an empty <a>.
    stub(boundOf(0.05));
    render(ModelDetailView, { props: gbmProps, ...mounted });
    expect(await screen.findByText(/lower bound/i)).toBeInTheDocument();
    expect(screen.getByText("motor-ad-frequency@7")).toBeInTheDocument();
  });

  it("says nothing about bounds on a model that is not one", async () => {
    stub(GBM_MODEL);
    render(ModelDetailView, { props: gbmProps, ...mounted });
    await screen.findByRole("table", { name: "Features and constraints" });
    expect(screen.queryByText(/bound/i)).toBeNull();
  });

  it("renders an EBM's shape functions rather than the GBM panel", async () => {
    // The arms are mutually exclusive branches off one narrowed spec. A view that reaches the
    // GBM branch for an EBM renders nothing at all, and the page looks merely empty.
    stub(EBM_MODEL);
    render(ModelDetailView, { props: { slug: "motor-severity" }, ...mounted });
    const table = await screen.findByRole("table", { name: "annual_mileage shape function" });
    expect(within(table).getByText("< 5000")).toBeInTheDocument();
    expect(screen.queryByRole("table", { name: "Features and constraints" })).toBeNull();
  });

  it("still says so when a model really is reserved and unfitted", async () => {
    stub({ ...GBM_MODEL, status: "draft", fit_result: null });
    render(ModelDetailView, { props: gbmProps, ...mounted });
    expect(await screen.findByText(/reserved but not yet fitted/i)).toBeInTheDocument();
  });

  it("asks for a transparency artifact for a booster, and not for a GLM", async () => {
    // FR-MODEL-33 makes the artifact an obligation for a non-GLM Model and says nothing
    // about a GLM. Fetching it anyway would 404 on every GLM page on the platform, which
    // reads as an outage in every log that counts 404s.
    const fetchMock = stubByUrl({
      "/api/v1/models/motor-ad-frequency": GBM_MODEL,
      [`/api/v1/models/${GBM_MODEL.id}/transparency`]: ARTIFACT,
      "/api/v1/models/motor-frequency": MODEL,
    });
    render(ModelDetailView, { props: gbmProps, ...mounted });
    await screen.findByText(/under-price/i);

    fetchMock.mockClear();
    render(ModelDetailView, { props: { slug: "motor-frequency" }, ...mounted });
    await screen.findByRole("table", { name: "Coefficients" });
    expect(fetchMock.mock.calls.map(String).join(" ")).not.toContain("transparency");
  });

  it("reads a model with no artifact built as a state, not as the error banner", async () => {
    // The one call on this page allowed to 404 without the page becoming an error. Routed
    // into `problem`, a booster whose artifact Job has not run yet renders a red banner
    // instead of the model.
    stubByUrl({ "/api/v1/models/motor-ad-frequency": GBM_MODEL });
    render(ModelDetailView, { props: gbmProps, ...mounted });
    expect(await screen.findByText(/no transparency artifact/i)).toBeInTheDocument();
    expect(screen.queryByRole("alert")).toBeNull();
    expect(screen.getByRole("table", { name: "Features and constraints" })).toBeInTheDocument();
  });

  it("says a GLM surrogate is a surrogate, and what its diagnostics are against", async () => {
    // FR-MODEL-96: a surrogate's diagnostics are against the source model's predictions,
    // never against observed claims. A page that omits it shows a fit statistic the reader
    // takes for fit to experience — and a surrogate is a GLM in every other visible respect,
    // so nothing else on the page distinguishes one.
    stub({
      ...MODEL,
      spec: {
        ...MODEL.spec,
        // Both halves, per FR-MODEL-102: the response column is what makes the id legal.
        response_column: "__gbm_prediction__",
        approximates_model_id: GBM_MODEL.id,
      },
    });
    render(ModelDetailView, { props: { slug: "motor-ad-frequency-approx" }, ...mounted });
    expect(await screen.findByText(/approximation of model/i)).toBeInTheDocument();
    expect(screen.getByText(/not against observed claims/i)).toBeInTheDocument();
  });

  it("says nothing about a surrogate on a GLM fitted to claims", async () => {
    render(ModelDetailView, { props, ...mounted });
    await screen.findByRole("table", { name: "Coefficients" });
    expect(screen.queryByText(/approximation of model/i)).toBeNull();
  });
});
