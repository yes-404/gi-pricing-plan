import { afterEach, describe, expect, it, vi } from "vitest";

import { isProblem, ProblemError } from "../problem";
import { getSystemStatus, type SystemStatus } from "../systemStatus";

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

describe("the system status client (07 §4.6)", () => {
  it("reads GET /api/v1/admin/status", async () => {
    const body: SystemStatus = {
      status: "up",
      components: [],
      schema_version: "e5b2a7d94c13",
      queues: [],
      blob_store: { objects: 0, bytes: 0 },
      caches: [],
    };
    respond(200, body);
    await expect(getSystemStatus()).resolves.toEqual(body);
    expect(String(vi.mocked(fetch).mock.calls[0]![0])).toMatch(/\/api\/v1\/admin\/status$/);
  });

  it("keeps null as null, so a view can tell 'could not be read' from 'none'", async () => {
    const body: SystemStatus = {
      status: "down",
      components: [],
      schema_version: null,
      queues: null,
      blob_store: null,
      caches: [],
    };
    respond(200, body);
    const status = await getSystemStatus();
    expect(status.schema_version).toBeNull();
    expect(status.queues).toBeNull();
    expect(status.blob_store).toBeNull();
  });

  it("surfaces a refusal as a ProblemError", async () => {
    respond(403, {
      type: "about:blank", title: "Forbidden", status: 403, code: "FORBIDDEN", errors: [],
    });
    await expect(getSystemStatus()).rejects.toSatisfy(
      (e: unknown) => e instanceof ProblemError && isProblem(e) && e.code === "FORBIDDEN",
    );
  });
});
