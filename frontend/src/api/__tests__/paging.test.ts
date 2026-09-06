import { afterEach, describe, expect, it, vi } from "vitest";

import { listModels, modelsForVersion, MODEL_PAGE_CAP, type Model } from "@/api/models";
import { pageThrough } from "@/api/paging";

function model(id: string, versionId: string) {
  return { id, dataset_version_id: versionId } as Model;
}

function stubPages(pages: { items: unknown[]; next_cursor: string | null }[]) {
  let call = 0;
  const fetch = vi.fn(async (url: unknown) => {
    void url;
    const page = pages[Math.min(call, pages.length - 1)]!;
    call += 1;
    return new Response(JSON.stringify({ ...page, total_estimate: 0 }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

afterEach(() => vi.unstubAllGlobals());

describe("pageThrough", () => {
  it("concatenates pages in the order the route returned them", async () => {
    // Order is load-bearing, not incidental: `Model` carries no timestamp, so "most
    // recent" exists only because the route orders by a UUIDv7 id. Anything here that
    // sorted would silently hand callers an arbitrary row with no error.
    stubPages([
      { items: [{ id: "c" }, { id: "b" }], next_cursor: "n1" },
      { items: [{ id: "a" }], next_cursor: null },
    ]);

    const result = await pageThrough<{ id: string }>("/things", {}, 5);

    expect(result.items.map((i) => i.id)).toEqual(["c", "b", "a"]);
    expect(result.truncated).toBe(false);
  });

  it("stops at the cap and reports that it did", async () => {
    const fetch = stubPages([{ items: [{ id: "x" }], next_cursor: "more" }]);

    const result = await pageThrough<{ id: string }>("/things", {}, 3);

    expect(fetch).toHaveBeenCalledTimes(3);
    expect(result.truncated).toBe(true);
  });

  it("does not report truncation when the list ends exactly at the cap", async () => {
    // The boundary between "stopped because there is no more" and "stopped because I was
    // told to". Reporting truncation here would warn about rows that do not exist.
    stubPages([
      { items: [{ id: "1" }], next_cursor: "n" },
      { items: [{ id: "2" }], next_cursor: null },
    ]);

    expect((await pageThrough<{ id: string }>("/things", {}, 2)).truncated).toBe(false);
  });
});

describe("models for a dataset version", () => {
  it("walks pages and keeps the route's newest-first order", async () => {
    stubPages([
      { items: [model("m3", "v1"), model("m2", "v9")], next_cursor: "n" },
      { items: [model("m1", "v1")], next_cursor: null },
    ]);

    const page = await listModels();

    // `m1` sits on page two, so a filter over page one alone would miss it — the defect
    // OQ-611 records. And the surviving order is the route's, so the caller's
    // default of "the first" means "the most recent".
    expect(modelsForVersion(page, "v1").map((m) => m.id)).toEqual(["m3", "m1"]);
  });

  it("returns an empty list distinguishably from a truncated one", async () => {
    // An empty selector must not be readable as "this version has no models" when the
    // walk simply stopped early.
    stubPages([{ items: [model("m1", "other")], next_cursor: "more" }]);

    const page = await listModels();

    expect(modelsForVersion(page, "v1")).toEqual([]);
    expect(page.truncated).toBe(true);
  });

  it("walks at most MODEL_PAGE_CAP pages", async () => {
    const fetch = stubPages([{ items: [], next_cursor: "endless" }]);

    await listModels();

    expect(fetch).toHaveBeenCalledTimes(MODEL_PAGE_CAP);
  });
});
