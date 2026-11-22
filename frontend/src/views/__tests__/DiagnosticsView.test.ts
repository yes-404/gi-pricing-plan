import { fireEvent, render, screen, waitFor, within } from "@testing-library/vue";
import { afterEach, describe, expect, it, vi } from "vitest";
import {
  createRouter,
  createWebHistory,
  type RouteLocationNormalizedLoaded,
} from "vue-router";

import type { Diagnostics, FactorFinerLevels } from "@/api/diagnostics";
import type { Model } from "@/api/models";
import { routes } from "@/router";

import DiagnosticsView from "../DiagnosticsView.vue";
import { DIAGNOSTICS, GBM_MODEL, GLM_MODEL } from "./fixtures";

/**
 * The three charts this view mounts are ECharts, and ECharts paints to a canvas jsdom does
 * not provide — every render leaks an unhandled `clearRect` on null out of the animation
 * loop. Vitest counts those as errors and exits 1 while still printing every test as passed,
 * so the file was red from the commit that mounted the charts and read as green.
 *
 * Stubbed rather than fixed with a canvas shim: each chart asserts its own `option` object in
 * its own file (`HistogramChart.test.ts:9-15` is the precedent), and what this file tests is
 * the tables and the fetches.
 */
vi.mock("vue-echarts", () => ({
  default: { name: "VChart", props: ["option"], template: "<div data-testid='chart' />" },
}));

const NOT_FOUND = {
  type: "about:blank",
  title: "Not Found",
  status: 404,
  code: "NOT_FOUND",
  detail: "No such model.",
};

function stubByUrl(routes: Record<string, { status?: number; body: unknown }>): ReturnType<typeof vi.fn> {
  const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    for (const [path, response] of Object.entries(routes)) {
      if (url.includes(path)) {
        return new Response(JSON.stringify(response.body), {
          status: response.status ?? 200,
          headers: { "content-type": "application/json" },
        });
      }
    }
    return new Response(JSON.stringify(NOT_FOUND), {
      status: 404,
      headers: { "content-type": "application/problem+json" },
    });
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

const mounted = { global: { stubs: { RouterLink: { template: "<a><slot /></a>" } } } };

/** The GLM arm of a diagnostics artifact: its presence is what makes the fit a GLM's. */
const GLM_ARM: NonNullable<Diagnostics["glm"]> = {
  deviance: 10,
  null_deviance: 20,
  dispersion: 1,
  degrees_of_freedom: 5,
  type_iii_tests: [],
  type_iii_omitted: [],
  monotonicity: [],
  monotonicity_omitted: [],
  aliasing: [],
  vif: {},
};

/**
 * The view reads two endpoints, not one: the artifact, and the model whose spec carries
 * `approximates_model_id`. `"/diagnostics"` is matched first because the model's own URL is a
 * prefix of the artifact's, so the looser key would answer both.
 */
function stubBoth(): ReturnType<typeof vi.fn> {
  return stubByUrl({
    "/diagnostics": { body: DIAGNOSTICS },
    "/models/motor-frequency": { body: GBM_MODEL },
  });
}

/**
 * `client.ts:31` builds `new URL(path, window.location.origin)`, so what reaches `fetch` is
 * always absolute — under jsdom, `http://localhost:3000/...`. The origin is jsdom
 * configuration rather than this view's behaviour, so it is dropped here instead of being
 * written into each expectation; `search` is kept, since the version query is the assertion.
 */
function pathOf(fetchMock: ReturnType<typeof vi.fn>): string {
  const url = new URL(String(fetchMock.mock.calls[0]?.[0]));
  return `${url.pathname}${url.search}`;
}

afterEach(() => vi.unstubAllGlobals());

describe("DiagnosticsView", () => {
  it("asks for the version it was routed with", async () => {
    const fetchMock = stubBoth();
    render(DiagnosticsView, { props: { slug: "motor-frequency", version: "3" }, ...mounted });
    await waitFor(() => expect(fetchMock).toHaveBeenCalled());
    expect(pathOf(fetchMock)).toBe("/api/v1/models/motor-frequency/diagnostics?version=3");
  });

  it("asks for the latest when it was routed without one", async () => {
    const fetchMock = stubBoth();
    render(DiagnosticsView, { props: { slug: "motor-frequency" }, ...mounted });
    await waitFor(() => expect(fetchMock).toHaveBeenCalled());
    expect(pathOf(fetchMock)).toBe("/api/v1/models/motor-frequency/diagnostics");
  });

  it("shows the problem detail when there are no diagnostics to show", async () => {
    stubByUrl({});
    render(DiagnosticsView, { props: { slug: "nope" }, ...mounted });
    expect(await screen.findByText(/no such model/i)).toBeInTheDocument();
  });

  it("shows the provenance badge, naming the Job that produced the diagnostics (FR-2159)", async () => {
    stubBoth();
    render(DiagnosticsView, { props: { slug: "motor-frequency" }, ...mounted });
    const badge = await screen.findByRole("group", { name: "Provenance" });
    expect(within(badge).getByText(DIAGNOSTICS.provenance.produced_by_job_id!)).toBeInTheDocument();
  });

  it("puts train and holdout side by side, each with its rows and overall A/E", async () => {
    stubBoth();
    render(DiagnosticsView, { props: { slug: "motor-frequency" }, ...mounted });
    const table = await screen.findByRole("table", { name: /headline metrics/i });
    expect(within(table).getAllByRole("columnheader").map((h) => h.textContent?.trim())).toEqual([
      "Metric",
      "Train",
      "Holdout",
    ]);
    const rows = within(table).getByRole("row", { name: /overall A\/E/i });
    const cells = within(rows).getAllByRole("cell");
    expect(cells[0]).toHaveTextContent("1.002");
    expect(cells[1]).toHaveTextContent("0.987");
  });

  it("shows no unseen-level section for a GBM, which refuses such a level whatever is declared", async () => {
    // FR-2143: a GBM's diagnostics never record the counts, so "not recorded" would be false.
    stubBoth();
    render(DiagnosticsView, { props: { slug: "motor-frequency" }, ...mounted });
    await screen.findByRole("table", { name: /headline metrics/i });

    expect(screen.queryByLabelText("Rows on a level this fit never saw")).not.toBeInTheDocument();
    expect(screen.queryByText(/not recorded/i)).not.toBeInTheDocument();
  });

  it("says rows on an unseen level were not recorded for a fit stored before the rule", async () => {
    // FR-2143: absent is "not recorded", never "none left out".
    stubByUrl({
      "/diagnostics": { body: { ...DIAGNOSTICS, glm: GLM_ARM } },
      "/models/motor-frequency": { body: GBM_MODEL },
    });
    render(DiagnosticsView, { props: { slug: "motor-frequency" }, ...mounted });
    const section = await screen.findByLabelText("Rows on a level this fit never saw");

    expect(section).toHaveTextContent("Holdout: not recorded");
    expect(section).not.toHaveTextContent("none left out");
    expect(section).toHaveTextContent("is refused");
  });

  it("states the count and exposure left out, and that a quote is refused", async () => {
    const withExcluded = {
      ...DIAGNOSTICS,
      glm: GLM_ARM,
      universal: {
        train: { ...DIAGNOSTICS.universal.train, rows_excluded_unseen_level: 0,
                 exposure_excluded_unseen_level: "0" },
        holdout: { ...DIAGNOSTICS.universal.holdout, rows_excluded_unseen_level: 50,
                   exposure_excluded_unseen_level: "50.0" },
      },
    };
    stubByUrl({
      "/diagnostics": { body: withExcluded },
      "/models/motor-frequency": { body: GBM_MODEL },
    });
    render(DiagnosticsView, { props: { slug: "motor-frequency" }, ...mounted });
    const section = await screen.findByLabelText("Rows on a level this fit never saw");

    expect(section).toHaveTextContent("Train: none left out");
    expect(section).toHaveTextContent("Holdout: 50 rows (exposure 50.0) are left out of every figure");
    expect(section).toHaveTextContent("A quote with such a level is refused");
  });

  it("labels how the metrics were weighted, which the fit had to record", async () => {
    stubBoth();
    render(DiagnosticsView, { props: { slug: "motor-frequency" }, ...mounted });
    expect(await screen.findByText(/exposure-weighted/i)).toBeInTheDocument();
  });

  it("does not warn about a surrogate denominator on a model that is not one", async () => {
    stubBoth();
    render(DiagnosticsView, { props: { slug: "motor-frequency" }, ...mounted });
    await screen.findByRole("table", { name: /headline metrics/i });
    expect(screen.queryByRole("note")).not.toBeInTheDocument();
  });

  /**
   * Every field `ResidualSummary` declares, named one by one rather than counted.
   *
   * The plan this slice was written from lists four — mean, std, minimum, maximum — and
   * `diagnostics.py:124-134` declares six. A row count would pass against the wrong six as
   * easily as the right ones, so the tails are asserted by name: `p01` and `p99` are what a
   * reviewer reads to see whether the fit misses at the extremes, and a residual table
   * showing only mean and std reports a narrower distribution than the fit recorded.
   */
  it("shows every field of the residual summary, tails included", async () => {
    stubBoth();
    render(DiagnosticsView, { props: { slug: "motor-frequency" }, ...mounted });
    const table = await screen.findByRole("table", { name: /residual summary/i });
    expect(within(table).getAllByRole("rowheader").map((cell) => cell.textContent?.trim())).toEqual(
      ["Mean", "Std dev", "Minimum", "Maximum", "P01", "P99"],
    );
    const tails = within(table).getByRole("row", { name: /p99/i });
    expect(within(tails).getAllByRole("cell")[0]).toHaveTextContent("0.71");
    expect(within(tails).getAllByRole("cell")[1]).toHaveTextContent("0.82");
  });

  /**
   * `glm` is null on this fixture, which is a GBM. The arm is guarded rather than always
   * mounted: `GlmDiagnostics` is not partitioned and has no empty form, so a panel rendered
   * for a model that has none would be a section of em dashes claiming a GLM was fitted.
   */
  it("does not show the GLM arm for a model that is not a GLM", async () => {
    stubBoth();
    render(DiagnosticsView, { props: { slug: "motor-frequency" }, ...mounted });
    await screen.findByRole("table", { name: /headline metrics/i });
    expect(screen.queryByRole("table", { name: /GLM fit statistics/i })).not.toBeInTheDocument();
  });

  it("does not call an unset complexity threshold a pass", async () => {
    stubBoth();
    render(DiagnosticsView, { props: { slug: "motor-frequency" }, ...mounted });
    const table = await screen.findByRole("table", { name: /complexity/i });
    const row = within(table).getByRole("row", { name: /factor count/i });
    expect(within(row).getAllByRole("cell")[1]).toHaveTextContent(/none set/i);
  });

  it("shows the two depth numbers, not just the mean", async () => {
    stubBoth();
    render(DiagnosticsView, { props: { slug: "motor-frequency" }, ...mounted });
    const table = await screen.findByRole("table", { name: /tree summary/i });
    expect(within(table).getByRole("row", { name: /max depth/i })).toHaveTextContent("6");
    expect(within(table).getByRole("row", { name: /mean depth/i })).toHaveTextContent("4.7");
  });

  /**
   * FR-199 sets `quantile_crossing` on the **second bound of a pair and nowhere else** —
   * including the first bound, which had nothing to cross. So `null` means "not a paired
   * quantile model", not "checked and clean", and a block reading `0 of 0 rows crossed` would
   * report a comparison that never happened. The same failure the complexity table's unset
   * threshold avoids.
   */
  it("says nothing about quantile crossing for a model that has no counterpart bound", async () => {
    stubBoth();
    render(DiagnosticsView, { props: { slug: "motor-frequency" }, ...mounted });
    await screen.findByRole("table", { name: /tree summary/i });
    expect(screen.queryByText(/quantile crossing/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/crossed the counterpart bound/i)).not.toBeInTheDocument();
  });

  it("reports the crossing count, the population and the worst gap together", async () => {
    stubByUrl({
      "/diagnostics": {
        body: {
          ...DIAGNOSTICS,
          gbm: {
            ...DIAGNOSTICS.gbm,
            quantile_crossing: {
              counterpart_model_id: "3f7c1d90-0000-4000-8000-000000000001",
              rows_checked: 120_000,
              rows_crossing: 41,
              worst_gap: 18.62,
            },
          },
        },
      },
      "/models/motor-frequency": { body: GBM_MODEL },
    });
    render(DiagnosticsView, { props: { slug: "motor-frequency" }, ...mounted });
    // All three numbers in one sentence: 41 rows crossing by a hair and 41 crossing by a
    // factor of ten are different findings, and a count alone describes them identically.
    expect(await screen.findByText(/41 of\s+120000 checked rows/i)).toBeInTheDocument();
    expect(screen.getByText(/worst gap\s+18\.62/i)).toBeInTheDocument();
    expect(screen.getByText(/3f7c1d90-0000-4000-8000-000000000001/)).toBeInTheDocument();
  });

  it("mounts the cross-validation panel when the artifact carries a path", async () => {
    stubBoth();
    render(DiagnosticsView, { props: { slug: "motor-frequency" }, ...mounted });
    expect(await screen.findByRole("table", { name: /regularisation path/i })).toBeInTheDocument();
    expect(screen.getByRole("table", { name: /fold dispersion/i })).toBeInTheDocument();
  });

  /**
   * The guard, proven the only way it can be. `CrossValidationDiagnostics` has no empty form —
   * `path` and `fold_metrics` are required and `folds` is `ge=2` — so a panel rendered for a
   * fit that was not cross-validated would not show an empty path, it would dereference
   * `null` and take the whole page down. `null` here is the artifact saying "this fit was
   * never cross-validated", which is a different claim from "it was, and scored nothing".
   */
  it("says nothing about cross-validation for a fit that was not cross-validated", async () => {
    stubByUrl({
      "/diagnostics": { body: { ...DIAGNOSTICS, cross_validation: null } },
      "/models/motor-frequency": { body: GBM_MODEL },
    });
    render(DiagnosticsView, { props: { slug: "motor-frequency" }, ...mounted });
    await screen.findByRole("table", { name: /tree summary/i });
    expect(screen.queryByRole("table", { name: /regularisation path/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("table", { name: /fold dispersion/i })).not.toBeInTheDocument();
    expect(screen.queryByText(/selected alpha/i)).not.toBeInTheDocument();
  });
});

/**
 * FR-109's finer level (`02` §5.3, "Diagnostics, finer level"; decision #1870 (b)). Read from
 * the stored `Diagnostics`, never computed here. The three cases of the maintainer's (c) on
 * #1506, each tested below: a model with no Factor on a chained grouping has no finer-level
 * section at all; one with such a Factor, fitted before the change (`finer_level_ae` null), says
 * "not available", never an empty table; one fitted after shows the tables. Which case a null
 * field is comes from the read's `chained_factors`, which the API composes by the fit's rule;
 * the view reads nothing else for it.
 */
describe("DiagnosticsView, finer level", () => {
  const REGION: FactorFinerLevels = {
    factor: "region",
    grouping: "region",
    levels: [
      {
        name: "postcode",
        cells: [
          { factor: "region", level: "AB1", actual: 30, expected: 20, ae: 1.5, exposure_years: "20" },
          { factor: "region", level: "AB2", actual: 10, expected: 20, ae: 0.5, exposure_years: "20" },
        ],
        unavailable_rows: 0,
        unavailable_exposure: "0",
        unavailable_actual: 0,
        unavailable_expected: 0,
      },
      {
        name: "area",
        cells: [
          { factor: "region", level: "AB", actual: 40, expected: 40, ae: 1, exposure_years: "40" },
        ],
        unavailable_rows: 3,
        unavailable_exposure: "2.5",
        unavailable_actual: 1,
        unavailable_expected: 2,
      },
    ],
  };

  /** `region`'s own A/E at the level it was fitted on, as the fit stores it for a term. */
  const REGION_FITTED = [
    { factor: "region", level: "NORTH", actual: 40, expected: 40, ae: 1, exposure_years: "40" },
  ];

  /**
   * The one top-level field, train and holdout alike (the maintainer's (B) on #1506). With
   * `fitted`, `region` is a term of the model and has its own A/E; without it, `region` is an
   * interaction's operand: finer levels, but no "as fitted" table.
   */
  function withFiner(finer: FactorFinerLevels[] | null, fitted = true): Diagnostics {
    const own = fitted ? REGION_FITTED : [];
    return {
      ...DIAGNOSTICS,
      universal: {
        train: {
          ...DIAGNOSTICS.universal.train,
          ae_by_factor: [...(DIAGNOSTICS.universal.train.ae_by_factor ?? []), ...own],
        },
        holdout: {
          ...DIAGNOSTICS.universal.holdout,
          ae_by_factor: [...(DIAGNOSTICS.universal.holdout.ae_by_factor ?? []), ...own],
        },
      },
      finer_level_ae: finer === null ? null : { train: finer, holdout: finer },
    };
  }

  /**
   * The artifact and the model. `chained` puts `region` in the read's `chained_factors`, as the
   * API does for a Factor on a grouping with a parent. No dataset version, Factor or Grouping
   * read is stubbed: the view must not need one (it would get a 404).
   */
  function serve(
    body: Diagnostics,
    { chained = false, model = GBM_MODEL }: { chained?: boolean; model?: Model } = {},
  ): ReturnType<typeof vi.fn> {
    return stubByUrl({
      "/diagnostics": { body: { ...body, chained_factors: chained ? ["region"] : [] } },
      "/models/motor-frequency": { body: model },
    });
  }

  it("offers a level selector for a factor on a chained grouping, and none for one that is not", async () => {
    serve(withFiner([REGION]), { chained: true });
    render(DiagnosticsView, { props: { slug: "motor-frequency" }, ...mounted });

    const selector = await screen.findByRole("combobox", { name: /level for region/i });
    expect(within(selector).getAllByRole("option").map((o) => o.textContent?.trim())).toEqual([
      "region (as fitted)",
      "postcode",
      "area",
    ]);
    // `vehicle_age` has an A/E of its own but no chain: it gets no selector.
    expect(screen.queryByRole("combobox", { name: /vehicle_age/i })).not.toBeInTheDocument();
  });

  it("offers no as-fitted level for an interaction's operand and opens on its finest level", async () => {
    serve(withFiner([REGION], false), { chained: true });
    render(DiagnosticsView, { props: { slug: "motor-frequency" }, ...mounted });

    const selector = await screen.findByRole("combobox", { name: /level for region/i });
    expect(within(selector).getAllByRole("option").map((o) => o.textContent?.trim())).toEqual([
      "postcode",
      "area",
    ]);
    const table = screen.getByRole("table", { name: /region at postcode, holdout/i });
    expect(within(table).getByRole("row", { name: /^AB1\b/ })).toBeInTheDocument();
  });

  it("shows a finer level's table with its named not-available row, count and exposure", async () => {
    serve(withFiner([REGION]), { chained: true });
    render(DiagnosticsView, { props: { slug: "motor-frequency" }, ...mounted });

    const selector = await screen.findByRole("combobox", { name: /level for region/i });
    await fireEvent.update(selector, "area");

    const table = await screen.findByRole("table", { name: /region at area, holdout/i });
    expect(within(table).getByRole("row", { name: /^AB\b/ })).toHaveTextContent("1");
    const missing = within(table).getByRole("row", { name: /not available/i });
    expect(missing).toHaveTextContent("3 rows");
    expect(missing).toHaveTextContent("2.5");
    expect(screen.getByRole("table", { name: /region at area, train/i })).toBeInTheDocument();
  });

  it.each([
    ["fitted after the change", withFiner([])],
    ["fitted before the change", withFiner(null)],
    ["stored before the change, no field at all", DIAGNOSTICS],
  ])("shows no finer-level section for a model with no factor on a chained grouping (%s)", async (_, body) => {
    serve(body);
    render(DiagnosticsView, { props: { slug: "motor-frequency" }, ...mounted });
    await screen.findByRole("table", { name: /headline metrics/i });

    expect(screen.queryByLabelText("Actual versus expected at a finer level")).not.toBeInTheDocument();
    expect(screen.queryByRole("combobox", { name: /level for/i })).not.toBeInTheDocument();
    expect(screen.queryByText(/not available/i)).not.toBeInTheDocument();
  });

  it("says not available, never an empty table, for a chained factor fitted before the change", async () => {
    serve(withFiner(null), { chained: true });
    render(DiagnosticsView, { props: { slug: "motor-frequency" }, ...mounted });

    const section = await screen.findByLabelText("Actual versus expected at a finer level");
    expect(section).toHaveTextContent("not available");
    expect(section).toHaveTextContent("region");
    expect(within(section).queryByRole("table")).not.toBeInTheDocument();
    expect(screen.queryByRole("combobox", { name: /level for/i })).not.toBeInTheDocument();
  });

  it("names the chained factors from the diagnostics read alone, with no definition read", async () => {
    const fetchMock = serve(withFiner(null), { chained: true });
    render(DiagnosticsView, { props: { slug: "motor-frequency" }, ...mounted });

    const section = await screen.findByLabelText("Actual versus expected at a finer level");
    expect(section).toHaveTextContent("Finer level for region");
    expect(section).toHaveTextContent("not available");
    const urls = fetchMock.mock.calls.map(([input]) => String(input));
    expect(urls.some((url) => /\/(dataset-versions|factors|groupings)\b/.test(url))).toBe(false);
  });

  it("shows the tables for a chained factor fitted after the change", async () => {
    serve(withFiner([REGION]), { chained: true });
    render(DiagnosticsView, { props: { slug: "motor-frequency" }, ...mounted });

    const section = await screen.findByLabelText("Actual versus expected at a finer level");
    expect(
      within(section).getByRole("table", { name: /region at region \(as fitted\), holdout/i }),
    ).toBeInTheDocument();
    expect(
      within(section).getByRole("table", { name: /region at region \(as fitted\), train/i }),
    ).toBeInTheDocument();
    expect(section).not.toHaveTextContent(/Finer level for .*: not available/);
  });

  /**
   * FR-141, under the maintainer's (c) on #1506: in a surrogate's finer-level table the "actual"
   * is the source model's prediction and the "expected" the surrogate's fitted mean. The view
   * labels it with the same notice as the surrogate's other actual-against-expected tables:
   * `SurrogateNotice`, rendered once in the page header for the whole page, which covers the
   * finer-level section with the rest. This holds the notice and the section on one page.
   */
  it("shows a surrogate's finer level under the page's FR-141 surrogate notice", async () => {
    const surrogate = {
      ...GLM_MODEL,
      spec: {
        ...GLM_MODEL.spec,
        response_column: "__gbm_prediction__",
        approximates_model_id: GBM_MODEL.id,
      },
    } as unknown as Model;
    serve({ ...withFiner([REGION]), glm: GLM_ARM }, { chained: true, model: surrogate });
    render(DiagnosticsView, { props: { slug: "motor-frequency" }, ...mounted });

    const section = await screen.findByLabelText("Actual versus expected at a finer level");
    expect(within(section).getAllByRole("table").length).toBeGreaterThan(0);
    const notice = screen.getByRole("note");
    expect(notice).toHaveTextContent("Its diagnostics are measured against that model's predictions");
    expect(notice).toHaveTextContent("not against observed claims");
  });
});

/**
 * The router is what is under test here, not the view. Every test above hands the view its
 * props directly, so all six would stay green against a route that never delivers
 * `?version=` — which is exactly the `/models/:slug` bug this entry was written not to
 * repeat.
 */
describe("the model-diagnostics route", () => {
  function propsFor(route: RouteLocationNormalizedLoaded): Record<string, unknown> {
    const record = route.matched[0];
    const toProps = record?.props?.default;
    return typeof toProps === "function"
      ? (toProps(route) as Record<string, unknown>)
      : route.params;
  }

  it("carries ?version= through to the view", async () => {
    const router = createRouter({ history: createWebHistory(), routes });
    await router.push("/models/motor-frequency/diagnostics?version=3");
    expect(router.currentRoute.value.name).toBe("model-diagnostics");
    expect(propsFor(router.currentRoute.value)).toEqual({ slug: "motor-frequency", version: "3" });
  });

  it("leaves the version undefined when the query is absent, so the latest is asked for", async () => {
    const router = createRouter({ history: createWebHistory(), routes });
    await router.push("/models/motor-frequency/diagnostics");
    expect(propsFor(router.currentRoute.value)).toEqual({
      slug: "motor-frequency",
      version: undefined,
    });
  });
});
