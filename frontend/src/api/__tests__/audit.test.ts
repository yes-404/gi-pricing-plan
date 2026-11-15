import { afterEach, describe, expect, it, vi } from "vitest";

import { exportAudit, getArtifactHistory, listAudit, verifyChain } from "../audit";

function respond(body: unknown, contentType = "application/json"): void {
  vi.stubGlobal(
    "fetch",
    vi.fn(
      async () =>
        new Response(typeof body === "string" ? body : JSON.stringify(body), {
          status: 200,
          headers: { "Content-Type": contentType },
        }),
    ),
  );
}

function lastUrl(): URL {
  return new URL(String(vi.mocked(fetch).mock.calls.at(-1)![0]));
}

afterEach(() => vi.unstubAllGlobals());

describe("audit (FR-371, FR-372)", () => {
  it("sends each filter and the cursor as a query parameter, and none that is unset", async () => {
    respond({ items: [], next_cursor: null, total_estimate: 0 });
    await listAudit({ action: "model.approved", entity: "model:motor@2", q: "ok" }, "c1");
    const query = Object.fromEntries(lastUrl().searchParams);
    expect(lastUrl().pathname).toBe("/api/v1/audit");
    expect(query).toEqual({ action: "model.approved", entity: "model:motor@2", q: "ok", cursor: "c1" });
  });

  it("verifies the whole chain with no range, and a span with one", async () => {
    respond({ intact: true });
    await verifyChain();
    expect(lastUrl().pathname).toBe("/api/v1/audit/verify");
    expect([...lastUrl().searchParams]).toEqual([]);
    await verifyChain({ from: "2026-01-01T00:00:00.000Z" });
    expect(Object.fromEntries(lastUrl().searchParams)).toEqual({ from: "2026-01-01T00:00:00.000Z" });
  });

  it("exports the current filters in the chosen format, as text", async () => {
    respond('{"sequence":1}\n', "application/x-ndjson");
    const text = await exportAudit({ actor: "u1", from: "2026-01-01T00:00:00.000Z" }, "json");
    expect(text).toBe('{"sequence":1}\n');
    expect(lastUrl().pathname).toBe("/api/v1/audit/export");
    expect(Object.fromEntries(lastUrl().searchParams)).toEqual({
      actor: "u1",
      from: "2026-01-01T00:00:00.000Z",
      format: "json",
    });
  });
});

describe("artifact history (FR-383)", () => {
  it("percent-encodes the ref into the path", async () => {
    respond({ ref: "model:motor@2", events: [] });
    await getArtifactHistory("model:motor@2");
    expect(lastUrl().pathname).toBe("/api/v1/artifacts/model%3Amotor%402/history");
  });
});
