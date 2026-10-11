import { afterEach, describe, expect, it, vi } from "vitest";

import { confirmEdit, getCellPage, getRateTable, previewEdit } from "../rateTables";

function respond(status: number, body: unknown): void {
  vi.stubGlobal(
    "fetch",
    vi.fn(
      async () =>
        new Response(JSON.stringify(body), {
          status,
          headers: { "Content-Type": "application/json" },
        }),
    ),
  );
}

function lastCall(): { url: string; method: string | undefined; body: unknown } {
  const [url, init] = vi.mocked(fetch).mock.calls.at(-1)!;
  return {
    url: String(url),
    method: init?.method,
    body: init?.body === undefined ? undefined : JSON.parse(String(init.body)),
  };
}

afterEach(() => vi.unstubAllGlobals());

describe("rateTables (FR-232)", () => {
  it("requests one cell page with the server cursor, and none without it", async () => {
    respond(200, { items: [], next_cursor: null, total_estimate: 0 });
    await getCellPage("area@3", "MTA");
    expect(lastCall().url).toContain("/api/v1/rate-tables/area@3/cells?cursor=MTA");
    await getCellPage("area@3");
    expect(lastCall().url).toMatch(/\/api\/v1\/rate-tables\/area@3\/cells$/);
  });

  it("reads a version's definition by its address", async () => {
    respond(200, { slug: "area", version: 3 });
    await getRateTable("area@3");
    expect(lastCall().url).toMatch(/\/api\/v1\/rate-tables\/area@3$/);
  });
});

describe("rateTables edits (FR-229)", () => {
  const body = {
    base_version: 3,
    change_note: "area A +5%",
    edits: [{ area: "A", relativity: "1.050000000000000001" }],
  };

  it("previews with confirm false and posts the edit values exactly as given", async () => {
    respond(200, { changed_cells: 1 });
    await previewEdit("area", body);
    const call = lastCall();
    expect(call.url).toMatch(/\/api\/v1\/rate-tables\/area\/versions$/);
    expect(call.method).toBe("POST");
    expect(call.body).toEqual({ ...body, confirm: false });
  });

  it("confirms with confirm true", async () => {
    respond(201, { version: 4 });
    await confirmEdit("area", body);
    expect(lastCall().body).toEqual({ ...body, confirm: true });
  });
});
