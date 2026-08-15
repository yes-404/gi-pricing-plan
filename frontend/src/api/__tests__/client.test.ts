import { afterEach, describe, expect, it, vi } from "vitest";

import { request } from "../client";
import { isProblem, ProblemError } from "../problem";

function respond(status: number, body: unknown, headers: Record<string, string> = {}): void {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () =>
      new Response(body === undefined ? null : JSON.stringify(body), {
        status,
        headers: { "Content-Type": "application/json", ...headers },
      }),
    ),
  );
}

afterEach(() => vi.unstubAllGlobals());

describe("the API client", () => {
  it("throws a ProblemError carrying the platform's code", async () => {
    respond(409, {
      type: "https://docs.gi-pricing.dev/errors/validation-has-failures",
      title: "The validation report did not pass",
      status: 409,
      code: "VALIDATION_HAS_FAILURES",
      detail: "`01` §1.3: there is no override.",
      errors: [],
      trace_id: "4266ca55704c00a04a7289c3946e3177",
    });

    const failure = await request("/datasets").catch((error: unknown) => error);
    expect(failure).toBeInstanceOf(ProblemError);
    expect(isProblem(failure, "VALIDATION_HAS_FAILURES")).toBe(true);
    expect((failure as ProblemError).traceId).toBe("4266ca55704c00a04a7289c3946e3177");
  });

  it("distinguishes two codes that share a status", async () => {
    // The reason clients branch on `code` and never on `status`: both are 409, and one
    // says fix the data while the other says an actuary must sign it off.
    respond(409, { title: "x", status: 409, code: "WARN_NOT_ACKNOWLEDGED", errors: [] });
    const failure = await request("/x").catch((error: unknown) => error);
    expect(isProblem(failure, "VALIDATION_HAS_FAILURES")).toBe(false);
    expect(isProblem(failure, "WARN_NOT_ACKNOWLEDGED")).toBe(true);
  });

  it("synthesises a distinguishable problem when the body is not one", async () => {
    // A proxy timing out in front of the API returns HTML. A client that assumed the
    // shape would throw `undefined.code` and hide the actual failure.
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response("<html>504</html>", { status: 504 })),
    );
    const failure = await request("/x").catch((error: unknown) => error);
    expect(isProblem(failure, "TRANSPORT_ERROR")).toBe(true);
    expect((failure as ProblemError).traceId).toBeUndefined();
  });

  it("sends Idempotency-Key as a header when asked", async () => {
    respond(202, { id: "job" });
    await request("/datasets/x/versions", {
      method: "POST",
      body: { blob: "a" },
      idempotencyKey: "retry-1",
    });

    const [, init] = vi.mocked(fetch).mock.calls[0] as [unknown, RequestInit];
    // `00` §5.4 specifies a header. A key in the query string is also a key in every
    // access log, and an HTTP client's automatic retry knows nothing about our query.
    expect((init.headers as Record<string, string>)["Idempotency-Key"]).toBe("retry-1");
  });

  it("omits an absent body rather than sending undefined", async () => {
    respond(200, { items: [] });
    await request("/datasets");
    const [, init] = vi.mocked(fetch).mock.calls[0] as [unknown, RequestInit];
    expect("body" in init).toBe(false);
  });
});
