import { render, screen, waitFor, within } from "@testing-library/vue";
import { afterEach, describe, expect, it, vi } from "vitest";
import {
  createRouter,
  createWebHistory,
  type RouteLocationNormalizedLoaded,
} from "vue-router";

import { routes } from "@/router";

import DiagnosticsView from "../DiagnosticsView.vue";
import { DIAGNOSTICS, GBM_MODEL } from "./fixtures";

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
   * FR-MODEL-78 sets `quantile_crossing` on the **second bound of a pair and nowhere else** —
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
