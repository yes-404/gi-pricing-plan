import { afterEach, describe, expect, it, vi } from "vitest";

import { ProblemError } from "../problem";
import { previewObjective } from "../objectives";

// SL-1275 (WK-690 Slice 5), RL-1616 DP-S5-1: `POST /api/v1/custom-objectives/preview`.
//
// The request/response field names below are PROVISIONAL: PL-1665 5.1' has the slice's
// first commit land the `model-schema` shapes (the request reuses `ObjectiveParameter`) and
// regenerate the client. Until then the argument is typed from the function itself, never
// from a hand-written interface. Re-read each fixture against the generated schema once it
// exists (vue-frontend: annotate fixtures with their generated type).
type PreviewRequest = Parameters<typeof previewObjective>[0];

const REQUEST = {
  loss: "w * where(exp(f) < y, w_under, w_over) * (y - exp(f)) ** 2",
  parameters: [
    { name: "w_under", type: "float", default: 2.0, min: 1, max: 10 },
    { name: "w_over", type: "float", default: 1.0, min: 0.1, max: 10 },
  ],
} as unknown as PreviewRequest;

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
    const fetch = stubResponse(200, { ok: true });

    const answer = await previewObjective(REQUEST);

    const [url, init] = fetch.mock.calls[0] as [unknown, { method?: string; body?: string }];
    expect(String(url)).toBe("/api/v1/custom-objectives/preview");
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body ?? "{}")).toEqual(REQUEST);
    expect((answer as { ok: boolean }).ok).toBe(true);
  });

  it("returns a parse failure as a value, not a throw (RL-1616: 200 with ok false)", async () => {
    // `numpy.where(...)` is WF-702 B1.5's example. The route answers 200 with `ok: false`
    // and the positioned error, as /model-specs/validate does; a client that threw on it
    // would turn every keystroke that does not yet parse into an error toast.
    stubResponse(200, {
      ok: false,
      error: { message: "attribute access is not in the grammar", position: 5 },
    });

    const answer = await previewObjective(REQUEST);

    expect((answer as { ok: boolean }).ok).toBe(false);
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
