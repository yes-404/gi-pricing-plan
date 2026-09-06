import { afterEach, describe, expect, it, vi } from "vitest";

import { listObjectives, OBJECTIVE_PAGE_CAP } from "../objectives";

function objective(slug: string) {
  return { id: slug, slug, version: 1, status: "approved" };
}

/** A fetch that hands back `pages` pages, each with a cursor except optionally the last. */
function stubPages(pages: { items: unknown[]; next_cursor: string | null }[]) {
  let call = 0;
  // The parameter is declared so `mock.calls[n][0]` is typed: a bare `vi.fn(async () =>
  // …)` gives an empty tuple, and the URL assertions below cannot index it.
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

describe("listObjectives", () => {
  it("follows the cursor and returns every page's objectives", () => {
    // The case OQ-605 is about: applicability is filtered client-side, so an
    // objective on page two is one the picker would otherwise never see.
    stubPages([
      { items: [objective("a")], next_cursor: "c1" },
      { items: [objective("b")], next_cursor: null },
    ]);

    return listObjectives().then((result) => {
      expect(result.items.map((o) => o.slug)).toEqual(["a", "b"]);
      expect(result.truncated).toBe(false);
    });
  });

  it("stops at the cap and reports that it did", async () => {
    // Every page carries a cursor, so paging never ends on its own.
    const fetch = stubPages([{ items: [objective("a")], next_cursor: "more" }]);

    const result = await listObjectives();

    expect(fetch).toHaveBeenCalledTimes(OBJECTIVE_PAGE_CAP);
    expect(result.truncated).toBe(true);
    expect(result.items).toHaveLength(OBJECTIVE_PAGE_CAP);
  });

  it("does not report truncation when the last page ends the list exactly at the cap", async () => {
    // The boundary that separates "stopped because there is no more" from "stopped
    // because I was told to". Reporting truncation here would make the picker warn about
    // objectives that do not exist.
    const pages = Array.from({ length: OBJECTIVE_PAGE_CAP }, (_unused, index) => ({
      items: [objective(`o${index}`)],
      next_cursor: index === OBJECTIVE_PAGE_CAP - 1 ? null : `c${index}`,
    }));
    stubPages(pages);

    const result = await listObjectives();

    expect(result.truncated).toBe(false);
    expect(result.items).toHaveLength(OBJECTIVE_PAGE_CAP);
  });

  it("passes a status filter to the server, which is the one axis it can filter", async () => {
    const fetch = stubPages([{ items: [], next_cursor: null }]);

    await listObjectives({ status: "certified" });

    expect(String(fetch.mock.calls[0]?.[0])).toContain("status=certified");
  });

  it("does not send a status parameter when none is given", async () => {
    const fetch = stubPages([{ items: [], next_cursor: null }]);

    await listObjectives();

    expect(String(fetch.mock.calls[0]?.[0])).not.toContain("status=");
  });
});
