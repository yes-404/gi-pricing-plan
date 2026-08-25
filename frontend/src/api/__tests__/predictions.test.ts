import { afterEach, describe, expect, it, vi } from "vitest";

import { intervalClaim, predict, unavailableCopy } from "@/api/predictions";

afterEach(() => {
  vi.unstubAllGlobals();
});

const MODEL_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa";

describe("predict", () => {
  it("POSTs the row wrapped in `rows` and returns the body", async () => {
    const body = { model_id: MODEL_ID, rows: [{ expected: 0.13 }] };
    const fetchMock = vi.fn(
      async (_input: RequestInfo | URL, _init?: RequestInit) =>
        new Response(JSON.stringify(body), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const result = await predict(MODEL_ID, { driver_age: 42 });

    expect(result).toEqual(body);
    const [url, init] = fetchMock.mock.calls[0]!;
    expect(String(url)).toContain(`/api/v1/models/${MODEL_ID}/predict`);
    expect(init!.method).toBe("POST");
    // `PredictRows` requires `rows` and sets `additionalProperties: false`.
    expect(JSON.parse(String(init!.body))).toEqual({ rows: [{ driver_age: 42 }] });
  });

  it("sends no Idempotency-Key: nothing is persisted, so there is nothing to deduplicate", async () => {
    const fetchMock = vi.fn(
      async (_input: RequestInfo | URL, _init?: RequestInit) =>
        new Response(JSON.stringify({ rows: [] }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await predict(MODEL_ID, {});

    const headers = fetchMock.mock.calls[0]![1]!.headers as Record<string, string>;
    expect(headers["Idempotency-Key"]).toBeUndefined();
  });
});

describe("unavailableCopy", () => {
  it("does not call covariance_not_stored a GBM reason (FR-MODEL-93)", () => {
    // FR-MODEL-93: "a fourth reason beside FR-MODEL-77's three and it is not one of them".
    expect(unavailableCopy("covariance_not_stored").family).toBe("glm");
    expect(unavailableCopy("no_interval_models_fitted").family).toBe("gbm");
    expect(unavailableCopy("interval_models_not_approved").family).toBe("gbm");
    expect(unavailableCopy("interval_models_stale").family).toBe("gbm");
    expect(unavailableCopy("model_type_has_no_interval").family).toBe("ebm");
  });

  it("reads `not_approved` as FR-MODEL-100(ii), not as unapproved outright", () => {
    // Asserted over the whole rendered copy rather than one field. FR-MODEL-100(ii) says the
    // reason "means the bounds are **less advanced than the model they bound**, not that
    // they are unapproved outright" — a constraint on what the reader is told, not on which
    // of the two strings tells them. Pinning it to `detail` would fail a copy that says it
    // in the headline, which is where the requirement's own phrasing naturally sits.
    const { headline, detail } = unavailableCopy("interval_models_not_approved");
    expect(`${headline} ${detail}`).toContain("less advanced");
    expect(`${headline} ${detail}`).not.toMatch(/\bnot approved\b/);
  });

  it("reads `stale` as FR-MODEL-100(iii): the central model is superseded", () => {
    const { headline, detail } = unavailableCopy("interval_models_stale");
    expect(`${headline} ${detail}`).toContain("superseded");
  });
});

describe("intervalClaim", () => {
  it("separates the two claims FR-MODEL-101 exists to keep apart", () => {
    // FR-MODEL-98: confidence_interval_mean covers E[Y|x].
    // FR-MODEL-101: quantile_pair_interval covers Y itself.
    expect(intervalClaim("confidence_interval_mean")).toContain("average");
    expect(intervalClaim("quantile_pair_interval")).toContain("individual");
    expect(intervalClaim("confidence_interval_mean")).not.toEqual(
      intervalClaim("quantile_pair_interval"),
    );
  });
});
