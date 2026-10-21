import { afterEach, describe, expect, it, vi } from "vitest";

import { ProblemError } from "../problem";
import { previewObjective, type ObjectivePreview, type ObjectivePreviewRequest } from "../objectives";

// SL-1275 (WK-690 Slice 5), RL-1616 DP-S5-1: `POST /api/v1/custom-objectives/preview`.
//
// The shapes are the generated ones (PL-1665 5.1' landed them in the slice's first commit):
// `REQUEST` is bound to `ObjectivePreviewRequest` and the answers to `ObjectivePreview`.

const REQUEST: ObjectivePreviewRequest = {
  loss: "w * where(exp(f) < y, w_under, w_over) * (y - exp(f)) ** 2",
  parameters: [
    { name: "w_under", type: "float", default: 2.0, min: 1, max: 10 },
    { name: "w_over", type: "float", default: 1.0, min: 0.1, max: 10 },
  ],
};

function stubResponse(status: number, body: unknown) {
  const fetch = vi.fn(async (url: unknown, init?: unknown) => {
    void url;
    void init;
    return new Response(JSON.stringify(body), {
      status,
      headers: { "Content-Type": status >= 400 ? "application/problem+json" : "application/json" },
    });
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

afterEach(() => vi.unstubAllGlobals());

describe("previewObjective", () => {
  it("posts the loss to the preview route and returns the answer", async () => {
    const body: ObjectivePreview = { ok: true };
    const fetch = stubResponse(200, body);

    const answer = await previewObjective(REQUEST);

    const [url, init] = fetch.mock.calls[0] as [unknown, { method?: string; body?: string }];
    // The client builds an absolute URL under jsdom, so the path is compared (diagnostics.test.ts).
    expect(new URL(String(url)).pathname).toBe("/api/v1/custom-objectives/preview");
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body ?? "{}")).toEqual(REQUEST);
    expect(answer.ok).toBe(true);
  });

  it("returns a parse failure as a value, not a throw (RL-1616: 200 with ok false)", async () => {
    // `numpy.where(...)` is WF-702 B1.5's example. The route answers 200 with `ok: false`
    // and the positioned error, as /model-specs/validate does; a client that threw on it
    // would turn every keystroke that does not yet parse into an error toast.
    const body: ObjectivePreview = {
      ok: false,
      error: { reason: "grammar", message: "attribute access is not in the grammar", line: 1, column: 5 },
    };
    stubResponse(200, body);

    const answer = await previewObjective(REQUEST);

    expect(answer.ok).toBe(false);
  });

  it.each([
    [403, "FORBIDDEN"],
    [409, "OBJECTIVE_KIND_NOT_ENABLED"],
    [422, "VALIDATION_FAILED"],
  ])("raises a ProblemError carrying the code on a %i (%s)", async (status, code) => {
    // The editor branches on the code, never the status (vue-frontend): 409 means the
    // flag is off, 422 is an over-bound grid refused before any SymPy work (3a).
    stubResponse(status, { type: "about:blank", title: code, status, code, errors: [] });

    await expect(previewObjective(REQUEST)).rejects.toSatisfy(
      (error: unknown) => error instanceof ProblemError && error.code === code,
    );
  });
});
