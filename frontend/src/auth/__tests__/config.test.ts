import { afterEach, describe, expect, it, vi } from "vitest";

import { loadAuthConfig } from "../config";

function respond(status: number, body: unknown): void {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () =>
      new Response(JSON.stringify(body), {
        status,
        headers: { "Content-Type": "application/json" },
      }),
    ),
  );
}

afterEach(() => vi.unstubAllGlobals());

describe("the auth config bootstrap", () => {
  // The module-level memoization shares one registry across tests in this file, so the
  // failure case must run first: a 503 with `cached` already set would resolve from the
  // cache and never fetch. (Plan Task 3's sample ran the memoize test first; reordered.)
  it("surfaces a failed fetch as a ProblemError", async () => {
    respond(503, { title: "Service Unavailable", status: 503, detail: "…", errors: [] });
    await expect(loadAuthConfig()).rejects.toThrow();
  });

  it("fetches the config once and memoizes it", async () => {
    const cfg = {
      issuer: "http://localhost:8080/realms/gi-pricing",
      client_id: "gi-pricing-frontend",
      dev_auth_enabled: true,
    };
    respond(200, cfg);
    expect(await loadAuthConfig()).toEqual(cfg);
    expect(await loadAuthConfig()).toEqual(cfg);
    expect(vi.mocked(fetch)).toHaveBeenCalledTimes(1);
  });
});
