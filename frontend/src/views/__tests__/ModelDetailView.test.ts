import { render, screen, within } from "@testing-library/vue";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createRouter, createWebHistory, type RouteLocationNormalizedLoaded } from "vue-router";

import { routes } from "@/router";

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
    // FR-113. Omitting it is how a reader ends up believing a factor has one fewer
    // level than it has.
    render(ModelDetailView, { props, ...mounted });
    const table = await screen.findByRole("table", { name: "area relativities" });

    const rural = within(table).getByText("rural").closest("tr")!;
    expect(within(rural).getByText("base")).toBeInTheDocument();
    expect(rural).toHaveTextContent("1.000");
    expect(within(table).getAllByRole("row")).toHaveLength(3); // header + two levels
  });

  it("says a model fitted before the report existed has not recorded its unseen levels", async () => {
    // FR-2143: absent is "not recorded", never "none".
    render(ModelDetailView, { props, ...mounted });
    const section = await screen.findByLabelText("Levels this fit never saw");

    expect(section).toHaveTextContent("Not recorded");
    expect(section).not.toHaveTextContent("None:");
  });

  it("lists, in words, a level the fit has no relativity for and what a quote does", async () => {
    stub({
      ...MODEL,
      fit_result: {
        ...MODEL.fit_result,
        unseen_level_gaps: [
          { factor: "age_band", level: "unknown", reached_by: ["null_value", "below_range"] },
        ],
      },
    });
    render(ModelDetailView, { props, ...mounted });
    const section = await screen.findByLabelText("Levels this fit never saw");

    expect(section).toHaveTextContent("age_band");
    expect(section).toHaveTextContent("unknown");
    expect(section).toHaveTextContent("a missing value or a value below the first boundary");
    expect(section).toHaveTextContent("is refused");
  });

  it("says what an empty list examined, and that a plain categorical level is not in it", async () => {
    // FR-2143: the list holds banded null levels and Grouping targets only, so "none" is scoped.
    stub({ ...MODEL, fit_result: { ...MODEL.fit_result, unseen_level_gaps: [] } });
    render(ModelDetailView, { props, ...mounted });
    const section = await screen.findByLabelText("Levels this fit never saw");

    expect(section).toHaveTextContent(
      "None among the missing-value levels of banded factors and the target levels of groupings",
    );
    expect(section).toHaveTextContent("A plain categorical level the fit never saw is not listed here");
    expect(section).toHaveTextContent("is refused");
    expect(section).not.toHaveTextContent("saw every level its factors can produce");
  });

  it("says an older model has not recorded the rows a grouping did not map, never that there are none", async () => {
    render(ModelDetailView, { props, ...mounted });
    const section = await screen.findByLabelText("Rows a grouping did not map");

    expect(section).toHaveTextContent("Not recorded");
    expect(section).not.toHaveTextContent("Every row");
  });

  it("states the rows and exposure a grouping did not map", async () => {
    stub({
      ...MODEL,
      fit_result: {
        ...MODEL.fit_result,
        grouping_unmapped: [
          { factor: "region", grouping: "region@2", rows: 10, exposure: "7.5" },
        ],
      },
    });
    render(ModelDetailView, { props, ...mounted });
    const section = await screen.findByLabelText("Rows a grouping did not map");

    expect(section).toHaveTextContent("region (region@2): 10 rows, exposure 7.5");
    expect(section).toHaveTextContent("does not map");
  });

  it("says an older model has not recorded its interaction cells, never that there are none", async () => {
    render(ModelDetailView, { props, ...mounted });
    const section = await screen.findByLabelText("Interaction cells this fit never saw");

    expect(section).toHaveTextContent("Not recorded");
    expect(section).not.toHaveTextContent("no interaction term");
  });

  it("says a fit with no interaction term has none", async () => {
    stub({ ...MODEL, fit_result: { ...MODEL.fit_result, unseen_cell_reports: [] } });
    render(ModelDetailView, { props, ...mounted });
    const section = await screen.findByLabelText("Interaction cells this fit never saw");

    expect(section).toHaveTextContent("This fit has no interaction term");
  });

  it("names the unfitted cells of a cross, the count and the cap, and what a quote does", async () => {
    stub({
      ...MODEL,
      fit_result: {
        ...MODEL.fit_result,
        unseen_cell_reports: [
          { factor: "age_x_fuel", state: "examined", producible: 6, unfitted: 3,
            examples: ["mid | Y", "unknown | X", "unknown | Y"], example_cap: 5 },
        ],
      },
    });
    render(ModelDetailView, { props, ...mounted });
    const section = await screen.findByLabelText("Interaction cells this fit never saw");

    expect(section).toHaveTextContent("3 of 6 cells");
    expect(section).toHaveTextContent("at most 5 are shown");
    expect(section).toHaveTextContent("mid | Y; unknown | X; unknown | Y");
    expect(section).toHaveTextContent("is refused");
  });

  it("says a cross with every cell fitted has none unfitted", async () => {
    stub({
      ...MODEL,
      fit_result: {
        ...MODEL.fit_result,
        unseen_cell_reports: [
          { factor: "age_x_fuel", state: "examined", producible: 6, unfitted: 0,
            examples: [], example_cap: 5 },
        ],
      },
    });
    render(ModelDetailView, { props, ...mounted });
    const section = await screen.findByLabelText("Interaction cells this fit never saw");

    expect(section).toHaveTextContent("all 6 cells");
  });

  it("says too many cells to name are not enumerated, and keeps the count", async () => {
    stub({
      ...MODEL,
      fit_result: {
        ...MODEL.fit_result,
        unseen_cell_reports: [
          { factor: "one_x_two", state: "count_only", producible: 10201, unfitted: 10200,
            examples: [], example_cap: 5 },
        ],
      },
    });
    render(ModelDetailView, { props, ...mounted });
    const section = await screen.findByLabelText("Interaction cells this fit never saw");

    expect(section).toHaveTextContent("10200 of 10201 cells");
    expect(section).toHaveTextContent("not enumerated");
  });

  it("says a lower bound is a floor, names pairings, and says unseen levels are not counted", async () => {
    stub({
      ...MODEL,
      fit_result: {
        ...MODEL.fit_result,
        unseen_cell_reports: [
          { factor: "area_x_fuel", state: "lower_bound", producible: 4, unfitted: 1,
            examples: ["A | y"], example_cap: 5 },
        ],
      },
    });
    render(ModelDetailView, { props, ...mounted });
    const section = await screen.findByLabelText("Interaction cells this fit never saw");

    expect(section).toHaveTextContent("at least 1 combinations of levels this fit saw");
    expect(section).toHaveTextContent("A | y");
    expect(section).toHaveTextContent("is refused");
    expect(section).toHaveTextContent("never saw at all are not counted");
  });

  it("says a full grid of seen levels has every combination fitted", async () => {
    stub({
      ...MODEL,
      fit_result: {
        ...MODEL.fit_result,
        unseen_cell_reports: [
          { factor: "area_x_fuel", state: "lower_bound", producible: 4, unfitted: 0,
            examples: [], example_cap: 5 },
        ],
      },
    });
    render(ModelDetailView, { props, ...mounted });
    const section = await screen.findByLabelText("Interaction cells this fit never saw");

    expect(section).toHaveTextContent("every combination of the levels this fit saw");
    expect(section).toHaveTextContent("never saw at all are not counted");
  });

  it("says a lower bound with too many pairings to name keeps the count", async () => {
    stub({
      ...MODEL,
      fit_result: {
        ...MODEL.fit_result,
        unseen_cell_reports: [
          { factor: "big_x_big", state: "lower_bound", producible: 90000, unfitted: 80000,
            examples: [], example_cap: 5 },
        ],
      },
    });
    render(ModelDetailView, { props, ...mounted });
    const section = await screen.findByLabelText("Interaction cells this fit never saw");

    expect(section).toHaveTextContent("at least 80000 combinations");
    expect(section).toHaveTextContent("not enumerated");
  });

  it("says a cross whose operands cannot be listed is not examined, with no count", async () => {
    stub({
      ...MODEL,
      fit_result: {
        ...MODEL.fit_result,
        unseen_cell_reports: [
          { factor: "area_x_fuel", state: "not_examined", producible: null, unfitted: null,
            examples: [], example_cap: 5 },
        ],
      },
    });
    render(ModelDetailView, { props, ...mounted });
    const section = await screen.findByLabelText("Interaction cells this fit never saw");

    expect(section).toHaveTextContent("not examined");
    expect(section).not.toHaveTextContent("cells its operands can produce have");
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

  it("links the predict screen with this model's slug and version", async () => {
    stub();
    render(ModelDetailView, {
      props,
      global: {
        stubs: {
          RouterLink: {
            props: ["to"],
            template: '<a :href="typeof to === \'string\' ? to : to.name"><slot /></a>',
          },
        },
      },
    });
    const link = await screen.findByText("Predict");
    expect(link.closest("a")!.getAttribute("href")).toBe("model-predict");
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
    // FR-199. Nothing else on this page distinguishes a bound from the central estimate:
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
    // FR-132 makes the artifact an obligation for a non-GLM Model and says nothing
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
    // FR-137: a surrogate's diagnostics are against the source model's predictions,
    // never against observed claims. A page that omits it shows a fit statistic the reader
    // takes for fit to experience — and a surrogate is a GLM in every other visible respect,
    // so nothing else on the page distinguishes one.
    stub({
      ...MODEL,
      spec: {
        ...MODEL.spec,
        // Both halves, per FR-141: the response column is what makes the id legal.
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

/**
 * The router, not the view. Every test above hands `ModelDetailView` its props directly, so
 * all of them stayed green while the route delivered `version` to nothing — `props: true` maps
 * `route.params` only, and `?version=` is a query. `02` §5.3 promises "`?version=` selects one;
 * the latest by default", and `QuantileBoundNotice` builds a link with that query and labels it
 * `slug@version`, so the link named one version and the page showed whichever was latest.
 */
describe("the model-detail route", () => {
  function propsFor(route: RouteLocationNormalizedLoaded): Record<string, unknown> {
    const record = route.matched[0];
    const toProps = record?.props?.default;
    return typeof toProps === "function"
      ? (toProps(route) as Record<string, unknown>)
      : route.params;
  }

  it("passes ?version= to the view, which is what selects a version", async () => {
    const router = createRouter({ history: createWebHistory(), routes });
    await router.push("/models/motor-frequency?version=3");
    expect(router.currentRoute.value.name).toBe("model-detail");
    expect(propsFor(router.currentRoute.value)).toEqual({ slug: "motor-frequency", version: "3" });
  });

  it("passes no version when none was asked for, so the latest is fetched", async () => {
    const router = createRouter({ history: createWebHistory(), routes });
    await router.push("/models/motor-frequency");
    expect(propsFor(router.currentRoute.value)).toEqual({
      slug: "motor-frequency",
      version: undefined,
    });
  });

  /**
   * Mine, not the plan's. `route.query.version` is `string | string[] | null`, and a repeated
   * key is what produces the array — reachable from a hand-edited or hand-shared URL. The
   * `typeof` guard is the whole reason the prop is not `String(route.query.version)`: that
   * would hand the view `"3,4"`, `Number` would make it `NaN`, and the request would go out
   * with a version nobody asked for. Ambiguous means unanswered, so it falls back to latest.
   */
  it("ignores a repeated ?version= rather than fetching the pair as one number", async () => {
    const router = createRouter({ history: createWebHistory(), routes });
    await router.push("/models/motor-frequency?version=3&version=4");
    expect(propsFor(router.currentRoute.value)).toEqual({
      slug: "motor-frequency",
      version: undefined,
    });
  });
});
