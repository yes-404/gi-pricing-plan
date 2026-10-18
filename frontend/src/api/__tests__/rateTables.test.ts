import { afterEach, describe, expect, it, vi } from "vitest";

import {
  bulkOperation,
  confirmEdit,
  confirmImport,
  exportCsv,
  getCellPage,
  getDiffCells,
  getRateTable,
  isJob,
  previewEdit,
  previewImport,
} from "../rateTables";

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

describe("rateTables diff cells (FR-231, FR-232)", () => {
  it("asks for one page of changed cells against a version, with the portfolio and the cursor", async () => {
    respond(200, { items: [], next_cursor: null, total_estimate: 0 });
    await getDiffCells("area@3", { against: "previous", portfolio: "7a1c", cursor: "MTA" });
    const url = new URL(lastCall().url, "http://x");
    expect(url.pathname).toBe("/api/v1/rate-tables/area@3/diff/cells");
    expect(Object.fromEntries(url.searchParams)).toEqual({
      against: "previous",
      portfolio: "7a1c",
      cursor: "MTA",
    });
  });

  it("sends neither portfolio nor cursor when they are not given", async () => {
    respond(200, { items: [], next_cursor: null, total_estimate: 0 });
    await getDiffCells("area@3", { against: "seed" });
    expect(new URL(lastCall().url, "http://x").searchParams.toString()).toBe("against=seed");
  });

  it("tells a 202 Job from a page by its shape", async () => {
    const job = { id: "j1", kind: "rate_table.diff_cells", status: "queued" };
    respond(202, job);
    const answer = await getDiffCells("area@3", { against: "previous" });
    expect(isJob(answer)).toBe(true);
    respond(200, { items: [], next_cursor: null, total_estimate: 0 });
    expect(isJob(await getDiffCells("area@3", { against: "previous" }))).toBe(false);
  });
});

describe("rateTables bulk operation (FR-233)", () => {
  it("posts the request exactly as given, decimals as strings", async () => {
    respond(201, { version: 4 });
    const request = { kind: "uplift_table", parameters: { percentage: "5.000000000000000001" } } as const;
    await bulkOperation("area@3", request);
    const call = lastCall();
    expect(call.url).toMatch(/\/api\/v1\/rate-tables\/area@3\/bulk-operation$/);
    expect(call.method).toBe("POST");
    expect(call.body).toEqual(request);
  });
});

describe("rateTables import and export (FR-235)", () => {
  const file = new File(["area,relativity\nA,1.05\n"], "area.csv", { type: "text/csv" });

  function formOf(): FormData {
    const init = vi.mocked(fetch).mock.calls.at(-1)![1]!;
    expect(init.body).toBeInstanceOf(FormData);
    expect(new Headers(init.headers).has("Content-Type")).toBe(false);
    return init.body as FormData;
  }

  it("previews an upload with confirm false", async () => {
    respond(200, { diff: { changed_cells: 1 }, created_by_import: {} });
    await previewImport("area@3", file);
    expect(String(vi.mocked(fetch).mock.calls.at(-1)![0])).toMatch(/\/api\/v1\/rate-tables\/area@3\/import$/);
    const form = formOf();
    expect(form.get("confirm")).toBe("false");
    expect((form.get("file") as File).name).toBe("area.csv");
  });

  it("confirms the same upload with confirm true", async () => {
    respond(201, { version: 4 });
    await confirmImport("area@3", file);
    expect(formOf().get("confirm")).toBe("true");
  });

  it("exports the CSV as text, not JSON", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response("area,relativity\nA,1.05\n", { status: 200, headers: { "Content-Type": "text/csv" } })),
    );
    expect(await exportCsv("area@3")).toBe("area,relativity\nA,1.05\n");
    expect(lastCall().url).toMatch(/\/api\/v1\/rate-tables\/area@3\/export\/csv$/);
  });
});
