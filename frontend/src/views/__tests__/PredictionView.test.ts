import { render, screen, waitFor } from "@testing-library/vue";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import PredictionView from "@/views/PredictionView.vue";

import { DRIVER_AGE_FACTOR, GLM_DATASET_VERSION, GLM_MODEL, PREDICTION } from "./fixtures";

vi.mock("@/components/PredictionUncertainty.vue", () => ({
  default: {
    name: "PredictionUncertainty",
    props: ["uncertainty", "row"],
    template: "<div data-testid='uncertainty'>{{ row.expected }}</div>",
  },
}));

const global = {
  stubs: { RouterLink: { props: ["to"], template: "<a><slot /></a>" } },
};

afterEach(() => {
  vi.unstubAllGlobals();
});

/**
 * Answer by URL. Modelled on `ModelComparisonView.test.ts`'s `stubByUrl` and kept separate
 * for the same reason it was: this page needs a POST that can answer 409 with a real problem
 * document, because every refusal branch here is a code, not a status.
 */
function stubByUrl(routes: Record<string, { status?: number; body: unknown }>): ReturnType<typeof vi.fn> {
  const fetchMock = vi.fn<(input: RequestInfo | URL, init?: RequestInit) => Promise<Response>>(async (input) => {
    const url = String(input);
    const key = Object.keys(routes).find((route) => url.includes(route));
    const match = key === undefined ? undefined : routes[key];
    if (match === undefined) {
      return new Response(
        JSON.stringify({ type: "about:blank", code: "NOT_FOUND", title: "Not found" }),
        { status: 404, headers: { "Content-Type": "application/json" } },
      );
    }
    return new Response(JSON.stringify(match.body), {
      status: match.status ?? 200,
      headers: { "Content-Type": "application/json" },
    });
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

function problem(code: string, status: number, detail: string) {
  return { status, body: { type: "about:blank", code, title: code, detail } };
}

// `/dataset-versions/` is answered because a Model carries only `dataset_version_id` while
// `listFactors` filters by `dataset_id`. Ordered before `/models/` is irrelevant here — the
// paths do not overlap — but the route must be present or the view cannot resolve its
// factors at all.
const LOADED = {
  "/dataset-versions/": { body: GLM_DATASET_VERSION },
  "/models/motor-ad-frequency": { body: GLM_MODEL },
  "/factors": { body: [DRIVER_AGE_FACTOR] },
};

describe("the input form", () => {
  it("asks for the model's source columns, not its factor ids", async () => {
    stubByUrl(LOADED);
    render(PredictionView, { props: { slug: "motor-ad-frequency" }, global });

    await waitFor(() => expect(screen.getByLabelText("driver_age_years")).toBeTruthy());
    // The offset column is caller-supplied too.
    expect(screen.getByLabelText("exposure_years")).toBeTruthy();
    expect(screen.queryByLabelText("f1")).toBeNull();
  });

  it("lists factors by dataset id, not by the version id the model carries", async () => {
    // A Model carries **only** `dataset_version_id`; `listFactors` filters by `dataset_id`;
    // and a Dataset Version is not a Dataset (`CLAUDE.md` §7). Passing one for the other
    // returns the wrong factor set against a real backend — and a stub that answers
    // `/factors` regardless of its query cannot see the difference, which is exactly why
    // this asserts the query string rather than the rendered form.
    const fetchMock = stubByUrl(LOADED);
    render(PredictionView, { props: { slug: "motor-ad-frequency" }, global });

    await waitFor(() => expect(screen.getByLabelText("driver_age_years")).toBeTruthy());
    const factorCall = fetchMock.mock.calls
      .map((call) => new URL(String(call[0])))
      .find((url) => url.pathname.endsWith("/factors"));
    expect(factorCall?.searchParams.get("dataset_id")).toBe(GLM_DATASET_VERSION.dataset_id);
    expect(factorCall?.searchParams.get("dataset_id")).not.toBe(GLM_MODEL.dataset_version_id);
  });
});

describe("scoring", () => {
  it("renders the expectation and hands the uncertainty to the panel", async () => {
    stubByUrl({ ...LOADED, "/predict": { body: PREDICTION } });
    render(PredictionView, { props: { slug: "motor-ad-frequency" }, global });

    await waitFor(() => expect(screen.getByLabelText("driver_age_years")).toBeTruthy());
    await userEvent.type(screen.getByLabelText("driver_age_years"), "42");
    await userEvent.type(screen.getByLabelText("exposure_years"), "1");
    await userEvent.click(screen.getByRole("button", { name: /score/i }));

    await waitFor(() => expect(screen.getByTestId("uncertainty").textContent).toContain("0.1342"));
  });

  it("shows no Job affordance: this route answers 200", async () => {
    stubByUrl({ ...LOADED, "/predict": { body: PREDICTION } });
    render(PredictionView, { props: { slug: "motor-ad-frequency" }, global });

    await waitFor(() => expect(screen.getByLabelText("driver_age_years")).toBeTruthy());
    expect(screen.queryByText(/queued|progress|job/i)).toBeNull();
  });
});

describe("the refusal taxonomy", () => {
  /**
   * Five codes share 409 and one shares 422 with two other messages, so every case here
   * asserts on the rendered copy rather than on a status. `problem.ts` states the rule on the
   * field: "Branch on this, never on `status`".
   */
  const cases: ReadonlyArray<[string, number, RegExp]> = [
    ["MODEL_NOT_FITTED", 409, /not been fitted/i],
    ["MODEL_INTERVAL_UNAVAILABLE", 409, /cross/i],
    ["MODEL_TYPE_UNSUPPORTED", 409, /spec and fit result disagree/i],
    ["MODEL_TERM_UNRESOLVED", 409, /cannot be scored/i],
    ["VALIDATION_FAILED", 422, /check the values/i],
  ];

  for (const [code, status, expected] of cases) {
    it(`names ${code} rather than showing a status`, async () => {
      stubByUrl({ ...LOADED, "/predict": problem(code, status, "detail from the server") });
      render(PredictionView, { props: { slug: "motor-ad-frequency" }, global });

      await waitFor(() => expect(screen.getByLabelText("driver_age_years")).toBeTruthy());
      await userEvent.click(screen.getByRole("button", { name: /score/i }));

      await waitFor(() => expect(screen.getByRole("alert").textContent).toMatch(expected));
      expect(screen.getByRole("alert").textContent).not.toContain(String(status));
    });
  }

  it("does not reorder crossed bounds into a displayable interval (FR-199)", async () => {
    // "detected, reported in the diagnostics, and never silently reordered". A view that
    // swapped them would show a plausible interval built from a refusal.
    stubByUrl({
      ...LOADED,
      "/predict": problem("MODEL_INTERVAL_UNAVAILABLE", 409, "The interval models cross"),
    });
    render(PredictionView, { props: { slug: "motor-ad-frequency" }, global });

    await waitFor(() => expect(screen.getByLabelText("driver_age_years")).toBeTruthy());
    await userEvent.click(screen.getByRole("button", { name: /score/i }));

    await waitFor(() => expect(screen.getByRole("alert")).toBeTruthy());
    expect(screen.queryByTestId("uncertainty")).toBeNull();
  });
});

describe("an offset-from-model spec", () => {
  it("asks for the referenced model's columns too", async () => {
    // The backend scores the referenced model on the caller's own frame, so a form built
    // from the central model alone would 409 on every submission.
    const central = {
      ...GLM_MODEL,
      spec: {
        ...GLM_MODEL.spec,
        offset: { kind: "model", offset_model_ref: "model:base-burning-cost@4" },
      },
    };
    const base = {
      ...GLM_MODEL,
      id: "ffffffff-ffff-4fff-8fff-ffffffffffff",
      model_family_slug: "base-burning-cost",
      spec: { ...GLM_MODEL.spec, factors: ["f2"], offset: { kind: "none" } },
    };
    const areaFactor = {
      ...DRIVER_AGE_FACTOR,
      id: "f2",
      slug: "area",
      source_columns: ["area_code"],
    };

    stubByUrl({
      "/dataset-versions/": { body: GLM_DATASET_VERSION },
      "/models/base-burning-cost": { body: base },
      "/models/motor-ad-frequency": { body: central },
      "/factors": { body: [DRIVER_AGE_FACTOR, areaFactor] },
    });
    render(PredictionView, { props: { slug: "motor-ad-frequency" }, global });

    await waitFor(() => expect(screen.getByLabelText("driver_age_years")).toBeTruthy());
    expect(screen.getByLabelText("area_code")).toBeTruthy();
  });
});
