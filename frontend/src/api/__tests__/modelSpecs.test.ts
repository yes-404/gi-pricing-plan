import { afterEach, describe, expect, it, vi } from "vitest";

import { ProblemError } from "@/api/problem";

import { validateSpec, type ModelSpec, type SpecValidation } from "../modelSpecs";

const SPEC = { model_type: "ebm", objective: "rmse" } as unknown as ModelSpec;

const REFUSED: SpecValidation = {
  ok: false,
  problems: [
    { kind: "response_missing", message: "no response column", subject: null },
    { kind: "split_missing", message: "no split named", subject: null },
  ],
  factor_count: 2,
  estimated_parameter_count: 14,
};

function stubFetch(status: number, body: unknown): ReturnType<typeof vi.fn> {
  const fetch = vi.fn(async () =>
    new Response(JSON.stringify(body), {
      status,
      headers: { "Content-Type": status >= 400 ? "application/problem+json" : "application/json" },
    }),
  );
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

afterEach(() => vi.unstubAllGlobals());

describe("validateSpec", () => {
  it("wraps the spec, because the body is ModelSpecValidate and not the spec itself", async () => {
    const fetch = stubFetch(200, { ok: true, problems: [], factor_count: 0,
      estimated_parameter_count: 0 });

    await validateSpec(SPEC);

    const sent = JSON.parse(String((fetch.mock.calls[0]?.[1] as RequestInit).body));
    expect(sent).toEqual({ spec: SPEC });
  });

  it("resolves a refused spec rather than throwing", async () => {
    // `02` §5.1: "a spec that merely cannot be fitted is not a bad *request*, so it is
    // not a 4xx". A 200 carrying `ok: false` is the answer to the question asked, and a
    // caller that treated it as a failure would show an error surface where the builder
    // should show problems.
    stubFetch(200, REFUSED);

    await expect(validateSpec(SPEC)).resolves.toMatchObject({ ok: false });
  });

  it("carries every problem, not the first", async () => {
    stubFetch(200, REFUSED);

    const result = await validateSpec(SPEC);

    expect(result.problems).toHaveLength(2);
    expect(result.problems.map((p) => p.kind)).toEqual(["response_missing", "split_missing"]);
  });

  it("throws for a spec naming a version that does not exist", async () => {
    // The same §5.1 row makes this a 404 — a different code path with a different
    // meaning, and the distinction the row exists to draw. A caller funnelling both
    // through one handler loses it.
    stubFetch(404, {
      title: "Not found", status: 404, code: "DATASET_VERSION_NOT_FOUND",
      detail: "No such version", errors: [],
    });

    await expect(validateSpec(SPEC)).rejects.toBeInstanceOf(ProblemError);
  });
});
