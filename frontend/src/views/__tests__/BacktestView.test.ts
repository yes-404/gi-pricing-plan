import { render, screen, within } from "@testing-library/vue";
import { afterEach, describe, expect, it, vi } from "vitest";

import BacktestView from "../BacktestView.vue";
import { BACKTEST, GBM_MODEL } from "./fixtures";

// Same reason as `DiagnosticsView.test.ts:14-24`: ECharts paints to a canvas happy-dom does
// not provide, and the unhandled `clearRect` on null exits vitest 1 while printing every test
// as passed. Each chart asserts its own `option` in its own file; this file tests the tables,
// the captions and the fetches.
vi.mock("vue-echarts", () => ({
  default: { name: "VChart", props: ["option"], template: "<div data-testid='chart' />" },
}));

const NOT_FOUND = {
  type: "about:blank",
  title: "Not Found",
  status: 404,
  code: "NOT_FOUND",
  detail: "No such backtest.",
};

function stubByUrl(
  routes: Record<string, { status?: number; body: unknown }>,
): ReturnType<typeof vi.fn> {
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
const props = { slug: "motor-frequency", backtestId: BACKTEST.id };

// `/models/backtests/` is matched before `/models/motor-frequency`, because the backtest path
// does not contain the slug at all and the looser key must not answer both.
function stubBoth(backtest: unknown = BACKTEST): ReturnType<typeof vi.fn> {
  return stubByUrl({
    "/models/backtests/": { body: backtest },
    "/models/motor-frequency": { body: GBM_MODEL },
  });
}

afterEach(() => vi.unstubAllGlobals());

describe("BacktestView", () => {
  it("fetches the backtest by its own id, not under the model", async () => {
    const fetchMock = stubBoth();
    render(BacktestView, { props, ...mounted });
    await screen.findByRole("table", { name: /headline metrics/i });
    const paths = fetchMock.mock.calls.map((call) => new URL(String(call[0])).pathname);
    expect(paths).toContain(`/api/v1/models/backtests/${BACKTEST.id}`);
  });

  // FR-MODEL-57's caption limb. This assertion is the only evidence that limb can have:
  // `req-coverage.py` scans backend tests and cannot see a frontend caption at all.
  it("captions the single partition Backtest, and shows no fit partition", async () => {
    stubBoth();
    render(BacktestView, { props, ...mounted });
    const table = await screen.findByRole("table", { name: /headline metrics/i });
    expect(within(table).getAllByRole("columnheader").map((h) => h.textContent?.trim())).toEqual([
      "Metric",
      "Backtest",
    ]);
    // "would claim a split nobody made" — neither fit label may appear anywhere in the view.
    expect(screen.queryByText(/holdout/i)).toBeNull();
    expect(screen.queryByText(/\btrain\b/i)).toBeNull();
  });

  it("shows the period the backtest covers", async () => {
    stubBoth();
    render(BacktestView, { props, ...mounted });
    expect(await screen.findByText(/2025-01-01 to 2025-12-31/)).toBeInTheDocument();
  });

  // Both period fields are optional and nullable, so this is an ordinary artifact and not an
  // error state. The view must not print an empty date.
  it("renders a backtest that declares no period", async () => {
    const undated = {
      ...BACKTEST,
      summary: { ...BACKTEST.summary, period_from: null, period_to: null },
    };
    stubBoth(undated);
    render(BacktestView, { props, ...mounted });
    await screen.findByRole("table", { name: /headline metrics/i });
    expect(screen.getByText(/no period declared/i)).toBeInTheDocument();
  });

  it("shows the problem detail when there is no such backtest", async () => {
    stubByUrl({});
    render(BacktestView, { props, ...mounted });
    expect(await screen.findByText(/no such backtest/i)).toBeInTheDocument();
  });

  // `residual_summary` is optional *and* nullable on `PartitionDiagnostics`, so a partition
  // carrying none is an ordinary artifact. Six blank rows would read as a measured
  // distribution of nothing; the table is dropped instead, as `DiagnosticsView` drops it.
  it("drops the residual table when the partition carries no summary", async () => {
    const bare = {
      ...BACKTEST,
      summary: {
        ...BACKTEST.summary,
        partition: { ...BACKTEST.summary.partition, residual_summary: null },
      },
    };
    stubBoth(bare);
    const { unmount } = render(BacktestView, { props, ...mounted });
    await screen.findByRole("table", { name: /headline metrics/i });
    expect(screen.queryByRole("table", { name: /residual summary/i })).toBeNull();

    // The control. Without it this assertion passes just as well when the table never
    // renders at all, which is a different defect wearing the same result.
    unmount();
    stubBoth();
    render(BacktestView, { props, ...mounted });
    expect(await screen.findByRole("table", { name: /residual summary/i }))
      .toBeInTheDocument();
  });
});
