import { fireEvent, render, screen, waitFor, within } from "@testing-library/vue";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { components } from "@/api/generated/schema";
import { formatMinor } from "@/components/dislocation/format";

import RegressionSuiteView from "../RegressionSuiteView.vue";

type RatingVersion = components["schemas"]["RatingVersion"];
type RegressionRun = components["schemas"]["RegressionRun"];
type RegressionRunSummary = components["schemas"]["RegressionRunSummary"];

/**
 * The view is exercised through the real `api/` modules with `fetch` stubbed: the tests
 * are about which requests the view makes (FR 8211 item (4) and (5): the run list, the run
 * by id, never a `POST`, never `…/cases` or `/blobs`), which a mocked client would skip.
 */

const push = vi.fn();
vi.mock("vue-router", () => ({
  RouterLink: { props: ["to"], template: "<a :href=\"to\"><slot /></a>" },
  useRouter: () => ({ push }),
}));

const RV_ID = "01a04394-0000-7000-8000-00000000001b";
const NEWEST = "01a04394-0000-7000-8000-0000000000c3";
const MIDDLE = "01a04394-0000-7000-8000-0000000000c2";
const OLDEST = "01a04394-0000-7000-8000-0000000000c1";

function summary(id: string, overall: "pass" | "fail", finished: string): RegressionRunSummary {
  return {
    id,
    job_id: null,
    overall,
    bundle_hash: `sha256:${"b".repeat(64)}`,
    suite_ref: "regression_suite:motor-gb-core@3",
    suite_content_hash: `sha256:${"a".repeat(64)}`,
    started_at: finished,
    finished_at: finished,
  };
}

function run(over: Partial<RegressionRun> = {}): RegressionRun {
  return {
    suite_ref: "regression_suite:motor-gb-core@3",
    suite_content_hash: `sha256:${"a".repeat(64)}`,
    rating_version_ref: "rating_version:motor-gb@27",
    bundle_hash: `sha256:${"b".repeat(64)}`,
    job_id: null,
    started_at: "2026-09-28T09:00:00Z",
    finished_at: "2026-09-28T09:00:04Z",
    overall: "fail",
    generation: { seed: 7, cases: 50, hypothesis_version: "6.165.7" },
    cases_blob: { sha256: "c".repeat(64), bytes: 10, media_type: "application/json" },
    golden_results: [
      { name: "young-driver-london", status: "pass", expected_minor: 112480, actual_minor: 112480, difference_minor: 0 },
      { name: "old-driver-leeds", status: "fail", expected_minor: 80000, actual_minor: 80150, difference_minor: 150 },
    ],
    property_results: [
      { name: "premium_positive", status: "pass", cases_run: 50, counterexample_minimal: false },
      {
        name: "monotone_in_age", status: "fail", cases_run: 50,
        counterexample: { driver_age: 25 }, counterexample_minimal: true,
        shrink: "completed", error_code: "PROPERTY_ASSERTION_FAILED",
      },
    ],
    ...over,
  };
}

const RATING: RatingVersion = {
  id: RV_ID,
  workspace_id: "01a04394-0000-7000-8000-000000000001",
  slug: "motor-gb",
  version: 27,
  status: "draft",
  dataset_version_id: "01a04394-0000-7000-8000-000000000002",
  model_ref: "model:fremtpl2-glm-7edfde@1",
  model_reference_mode: "exact",
  created_at: "2026-08-27T14:00:00Z",
  created_by: "01a04394-0000-7000-8000-000000000003",
  updated_at: "2026-08-27T14:05:00Z",
};

interface Stub {
  rating?: RatingVersion | Response;
  /** one entry per list page, in order. */
  pages?: { items: RegressionRunSummary[]; next_cursor: string | null }[];
  runs?: Record<string, RegressionRun>;
}

function json(body: unknown): Response {
  return new Response(JSON.stringify(body), { status: 200, headers: { "Content-Type": "application/json" } });
}

function problem(status: number, code: string, detail: string): Response {
  return new Response(
    JSON.stringify({ type: "about:blank", title: "Refused", status, code, detail, errors: [], trace_id: "abc123" }),
    { status, headers: { "Content-Type": "application/problem+json" } },
  );
}

function stubFetch(stub: Stub) {
  let page = 0;
  const calls: { method: string; url: URL }[] = [];
  const fetch = vi.fn(async (input: unknown, init?: RequestInit) => {
    const url = new URL(String(input), "http://localhost");
    calls.push({ method: init?.method ?? "GET", url });
    if (url.pathname === "/api/v1/rating-versions/motor-gb@27") return stub.rating instanceof Response ? stub.rating : json(stub.rating ?? RATING);
    if (url.pathname === `/api/v1/rating-versions/${RV_ID}/regression-runs`) {
      const pages = stub.pages ?? [{ items: [], next_cursor: null }];
      const body = pages[Math.min(page, pages.length - 1)]!;
      page += 1;
      return json({ ...body, total_estimate: 0 });
    }
    const byId = /regression-runs\/([^/]+)$/.exec(url.pathname);
    if (byId && stub.runs?.[byId[1]!]) return json(stub.runs[byId[1]!]);
    throw new Error(`unexpected request: ${init?.method ?? "GET"} ${url.pathname}`);
  });
  vi.stubGlobal("fetch", fetch);
  return { fetch, calls };
}

const LIST = [
  summary(NEWEST, "fail", "2026-09-28T09:20:00Z"),
  summary(MIDDLE, "pass", "2026-09-28T09:10:00Z"),
  summary(OLDEST, "pass", "2026-09-28T09:00:00Z"),
];

const props = { slug: "motor-gb", version: "27" };

beforeEach(() => push.mockReset());
afterEach(() => vi.unstubAllGlobals());

describe("the Regression suite view (FR 8211)", () => {
  it("opens the newest run by default and shows its golden quotes as money from minor units", async () => {
    const { calls } = stubFetch({ pages: [{ items: LIST, next_cursor: null }], runs: { [NEWEST]: run() } });
    render(RegressionSuiteView, { props });

    const table = await screen.findByRole("table", { name: /golden quotes/i });
    const passRow = within(table).getByText("young-driver-london").closest("tr")!;
    expect(within(passRow).getByText("pass")).toBeInTheDocument();
    expect(within(passRow).getAllByText(formatMinor(112480))).toHaveLength(2); // expected, actual
    const failRow = within(table).getByText("old-driver-leeds").closest("tr")!;
    expect(within(failRow).getByText("fail")).toBeInTheDocument();
    expect(within(failRow).getByText(formatMinor(80000))).toBeInTheDocument();
    expect(within(failRow).getByText(formatMinor(80150))).toBeInTheDocument();
    expect(within(failRow).getByText(formatMinor(150))).toBeInTheDocument();
    expect(calls.map((c) => c.url.pathname)).toContain(`/api/v1/rating-versions/${RV_ID}/regression-runs/${NEWEST}`);
  });

  it("?run=<id> selects that run instead of the newest", async () => {
    const { calls } = stubFetch({
      pages: [{ items: LIST, next_cursor: null }],
      runs: { [OLDEST]: run({ overall: "pass", golden_results: [{ name: "only-oldest", status: "pass", expected_minor: 1, actual_minor: 1, difference_minor: 0 }] }) },
    });
    render(RegressionSuiteView, { props: { ...props, run: OLDEST } });

    expect(await screen.findByText("only-oldest")).toBeInTheDocument();
    expect(calls.some((c) => c.url.pathname.endsWith(`/regression-runs/${NEWEST}`))).toBe(false);
  });

  it("marks the run the version's evidence names, even when it is not the newest", async () => {
    stubFetch({
      rating: { ...RATING, evidence: { regression_suite_run_id: MIDDLE } },
      pages: [{ items: LIST, next_cursor: null }],
      runs: { [NEWEST]: run() },
    });
    render(RegressionSuiteView, { props });

    const picker = await screen.findByLabelText("Regression run");
    const options = within(picker).getAllByRole("option");
    expect(options.map((o) => o.getAttribute("value"))).toEqual([NEWEST, MIDDLE, OLDEST]);
    expect(options[1]!.textContent).toMatch(/approval evidence/i);
    expect(options[0]!.textContent).not.toMatch(/approval evidence/i);
  });

  it("choosing a run in the picker cites it in ?run=", async () => {
    stubFetch({ pages: [{ items: LIST, next_cursor: null }], runs: { [NEWEST]: run() } });
    render(RegressionSuiteView, { props });

    await fireEvent.update(await screen.findByLabelText("Regression run"), MIDDLE);
    expect(push).toHaveBeenCalledWith({ query: { run: MIDDLE } });
  });

  it("shows a counterexample whose shrink completed, and labels an unminimised one", async () => {
    stubFetch({
      pages: [{ items: LIST, next_cursor: null }],
      runs: {
        [NEWEST]: run({
          property_results: [
            { name: "monotone_in_age", status: "fail", cases_run: 50, counterexample: { driver_age: 25 }, counterexample_minimal: true, shrink: "completed", error_code: "PROPERTY_ASSERTION_FAILED" },
            { name: "premium_bounded", status: "fail", cases_run: 50, counterexample: { driver_age: 90 }, counterexample_minimal: false, shrink: "stopped_on_limit", error_code: "PROPERTY_ASSERTION_FAILED" },
          ],
        }),
      },
    });
    render(RegressionSuiteView, { props });

    const minimal = await screen.findByLabelText("Counterexample of monotone_in_age");
    expect(minimal.textContent).toContain("driver_age");
    const raw = screen.getByLabelText("Counterexample of premium_bounded");
    expect(raw.textContent).toContain("driver_age");
    const rows = screen.getAllByRole("row");
    const rowOfBounded = rows.find((r) => r.textContent?.includes("premium_bounded"))!;
    const rowOfMonotone = rows.find((r) => r.textContent?.includes("monotone_in_age"))!;
    expect(within(rowOfBounded).getByText(/unminimised/i)).toBeInTheDocument();
    expect(within(rowOfMonotone).queryByText(/unminimised/i)).not.toBeInTheDocument();
  });

  it("shows no counterexample for a MONOTONE_NO_COMPARABLE_PAIRS failure", async () => {
    stubFetch({
      pages: [{ items: LIST, next_cursor: null }],
      runs: {
        [NEWEST]: run({
          property_results: [
            { name: "monotone_in_age", status: "fail", cases_run: 0, counterexample: null, counterexample_minimal: false, shrink: "completed", error_code: "MONOTONE_NO_COMPARABLE_PAIRS" },
          ],
        }),
      },
    });
    render(RegressionSuiteView, { props });

    expect(await screen.findByText("MONOTONE_NO_COMPARABLE_PAIRS")).toBeInTheDocument();
    expect(screen.queryByLabelText(/counterexample of/i)).not.toBeInTheDocument();
  });

  it("reads not_checked golden evidence as no golden quotes were checked", async () => {
    stubFetch({
      rating: {
        ...RATING,
        evidence: {
          golden_quotes: {
            status: "not_checked", regression_suite: "none",
            message: "no golden quotes were checked", reason: "no_suite_for_algorithm",
          },
        },
      },
      pages: [{ items: LIST, next_cursor: null }],
      runs: { [NEWEST]: run({ golden_results: [] }) },
    });
    render(RegressionSuiteView, { props });

    expect(await screen.findByText(/no golden quotes were checked/i)).toBeInTheDocument();
    expect(screen.queryByRole("table", { name: /golden quotes/i })).not.toBeInTheDocument();
  });

  it("makes no POST and reads neither the case log nor /blobs (DP-S11-2, FR-1221)", async () => {
    const { calls } = stubFetch({ pages: [{ items: LIST, next_cursor: null }], runs: { [NEWEST]: run() } });
    render(RegressionSuiteView, { props });
    await screen.findByRole("table", { name: /golden quotes/i });

    expect(calls.filter((c) => c.method !== "GET")).toEqual([]);
    expect(calls.filter((c) => /\/cases$|\/blobs/.test(c.url.pathname))).toEqual([]);
    expect(screen.queryByRole("button", { name: /run suite/i })).not.toBeInTheDocument();
  });

  it("reads an empty run list as such and requests no run", async () => {
    const { calls } = stubFetch({ pages: [{ items: [], next_cursor: null }] });
    render(RegressionSuiteView, { props });

    expect(await screen.findByText("No regression runs.")).toHaveAttribute("role", "status");
    expect(calls.some((c) => /regression-runs\/[^/]+$/.test(c.url.pathname))).toBe(false);
  });

  it("loads runs beyond one page through the cursor", async () => {
    const { calls } = stubFetch({
      pages: [
        { items: [LIST[0]!, LIST[1]!], next_cursor: "page-2" },
        { items: [LIST[2]!], next_cursor: null },
      ],
      runs: { [NEWEST]: run() },
    });
    render(RegressionSuiteView, { props });

    const picker = await screen.findByLabelText("Regression run");
    await waitFor(() => expect(within(picker).getAllByRole("option")).toHaveLength(3));
    const listCalls = calls.filter((c) => c.url.pathname.endsWith("/regression-runs"));
    expect(listCalls[1]!.url.searchParams.get("cursor")).toBe("page-2");
  });

  it("shows the platform's problem when the version is unknown", async () => {
    stubFetch({ rating: problem(404, "NOT_FOUND", "No such rating version.") });
    render(RegressionSuiteView, { props });

    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent("No such rating version."),
    );
  });
});
