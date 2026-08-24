import { render, screen, waitFor } from "@testing-library/vue";
import { afterEach, describe, expect, it, vi } from "vitest";

import { router } from "@/router";
import ModelComparisonView from "@/views/ModelComparisonView.vue";

import { COMPARISON } from "./fixtures";

// The three panels are tested in their own files; stub them so this test is about the state
// machine. ProfileView.test.ts is the precedent for the template-stub shape.
vi.mock("@/components/ComparisonMetricTable.vue", () => ({
  default: {
    name: "ComparisonMetricTable",
    props: ["metrics", "modelRefs"],
    template: "<div data-testid='metrics' />",
  },
}));
vi.mock("@/components/DoubleLiftChart.vue", () => ({
  default: { name: "DoubleLiftChart", props: ["series"], template: "<div data-testid='double-lift' />" },
}));
vi.mock("@/components/RelativityDiffTable.vue", () => ({
  default: {
    name: "RelativityDiffTable",
    props: ["differences", "modelRefs"],
    template: "<div data-testid='relativity' />",
  },
}));

const routeQuery: { ids?: string } = {};
vi.mock("vue-router", async (importOriginal) => ({
  ...(await importOriginal<typeof import("vue-router")>()),
  useRoute: () => ({ query: routeQuery }),
}));
const global = {
  stubs: { RouterLink: { props: ["to"], template: "<a :href='to'><slot /></a>" } },
};


const IDS = "11111111-1111-4111-8111-111111111111,22222222-2222-4222-8222-222222222222";
const COMPARISON_REF = `model_comparison:${COMPARISON.id}`;

/**
 * A fetch stub that answers by URL, because this page makes three different calls.
 *
 * Modelled on `ModelDetailView.test.ts:64`'s `stubByUrl` and **deliberately not shared with
 * it**: that one is `Record<string, unknown>` and always answers 200, which cannot express
 * the 202 the POST returns or the 409 a refusal returns — both of which this page branches
 * on. Its behaviour for an unstubbed URL is kept exactly, a real problem document carrying
 * `code: "NOT_FOUND"`, because views branch on the code and never on the status.
 */
function stubByUrl(routes: Record<string, { status?: number; body: unknown }>): void {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      const key = Object.keys(routes).find((path) => url.includes(path));
      const hit = key ? routes[key] : undefined;
      const body = hit?.body ?? {
        type: "about:blank",
        title: "Not found",
        status: 404,
        code: "NOT_FOUND",
      };
      return new Response(JSON.stringify(body), {
        status: hit?.status ?? 404,
        headers: { "Content-Type": "application/json" },
      });
    }),
  );
}

// `kind` is `model.compare` and not `model_compare`: the generated `JobKind` union is dotted
// throughout. Nothing validates this body at runtime, so a wrong literal here would have sat
// in the fixture unchallenged.
function job(status: string, ref: string | null = null): unknown {
  return {
    id: "1a2b3c4d-5555-4666-8777-888899990000",
    kind: "model.compare",
    status,
    result: ref ? { kind: "artifact", ref } : null,
    error:
      status === "failed"
        ? {
            code: "SPLIT_MISMATCH",
            message: "The models do not share a holdout.",
            retryable: false,
          }
        : null,
  };
}

afterEach(() => {
  vi.unstubAllGlobals();
  delete routeQuery.ids;
});

describe("ModelComparisonView", () => {
  it("declares /models/compare as a static route that wins over /models/:slug", () => {
    // Both routes match this path. Vue Router ranks static above dynamic, but a model whose
    // slug is literally `compare` is legal under refs.py's slug pattern, so the resolution is
    // asserted rather than assumed.
    expect(router.resolve("/models/compare").name).toBe("model-comparison");
    expect(router.resolve("/models/motor-ad-frequency").name).toBe("model-detail");
  });

  it("posts, polls, then fetches the artifact the job names", async () => {
    routeQuery.ids = IDS;
    stubByUrl({
      "/models/compare": { status: 202, body: job("queued") },
      "/jobs/": { status: 200, body: job("succeeded", COMPARISON_REF) },
      [`/models/comparisons/${COMPARISON.id}`]: { status: 200, body: COMPARISON },
    });
    render(ModelComparisonView, { props: { pollIntervalMs: 0 }, global });

    await waitFor(() => expect(screen.getByTestId("metrics")).toBeInTheDocument());
    expect(screen.getByTestId("double-lift")).toBeInTheDocument();
    expect(screen.getByTestId("relativity")).toBeInTheDocument();
    // FR-DATA-36 makes the shared holdout stored rather than promised, and §4.11 keeps the
    // SplitRef "so the claim is checkable by a reader". The reader has to be shown it.
    expect(screen.getByText(/169503/)).toBeInTheDocument();
  });

  // `waitForJob` returns the job in whatever state it is in, so a failed job arrives through
  // the success path. Its `error.message` is the only thing that says what went wrong.
  it("shows a failed job's message, and does not fetch an artifact", async () => {
    routeQuery.ids = IDS;
    stubByUrl({
      "/models/compare": { status: 202, body: job("queued") },
      "/jobs/": { status: 200, body: job("failed") },
    });
    render(ModelComparisonView, { props: { pollIntervalMs: 0 }, global });

    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent(/do not share a holdout/),
    );
    expect(screen.queryByTestId("metrics")).toBeNull();
  });

  // The state `waitForJob`'s own doc comment warns about: attempts ran out and the job is
  // still running. It is NOT a failure, and telling a user the comparison failed when it is
  // still computing is the specific misreading that comment exists to prevent.
  it("distinguishes 'still running' from 'failed' when the poll budget runs out", async () => {
    routeQuery.ids = IDS;
    stubByUrl({
      "/models/compare": { status: 202, body: job("queued") },
      "/jobs/": { status: 200, body: job("running") },
    });
    render(ModelComparisonView, { props: { pollIntervalMs: 0, pollAttempts: 3 }, global });

    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent(/still running/i));
    expect(screen.queryByRole("alert")).toBeNull();
  });

  // The comparability rules are answered by the POST before a Job exists, so a 409 here is a
  // complete answer and must be shown as one rather than retried.
  it("shows the problem document when the comparison is refused", async () => {
    routeQuery.ids = IDS;
    stubByUrl({
      "/models/compare": {
        status: 409,
        body: {
          type: "about:blank",
          title: "Models do not share a split",
          status: 409,
          code: "CONFLICT",
          detail: "motor-ad-frequency-gbm@2 was fitted on a different split.",
        },
      },
    });
    render(ModelComparisonView, { props: { pollIntervalMs: 0 }, global });

    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent("Models do not share a split"),
    );
  });

  // FR-MODEL-56 compares "two or more". One id is a diagnostics read, and the endpoint would
  // 422 it — refusing before the request makes that a sentence rather than a stack trace.
  it("refuses fewer than two ids without calling the API", async () => {
    routeQuery.ids = "11111111-1111-4111-8111-111111111111";
    const fetchSpy = vi.fn();
    vi.stubGlobal("fetch", fetchSpy);
    render(ModelComparisonView, { props: { pollIntervalMs: 0 }, global });

    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent(/two or more/i));
    expect(fetchSpy).not.toHaveBeenCalled();
  });
});
