import { afterEach, describe, expect, it, vi } from "vitest";

import { PAGE_SIZE } from "@/api/paging";
import { listRules, type ValidationRule } from "@/api/rules";

/** VR-DST-1 as a seeded row returns it: approved by construction, `warn_above` in params. */
const RULE: ValidationRule = {
  id: "33333333-3333-4333-8333-333333333333",
  slug: "psi-column",
  version: 1,
  layer: "distributional",
  check: "psi_column",
  severity: "warn",
  message: "Per-column PSI against the reference version",
  rationale: "",
  status: "approved",
  catalogue_id: "VR-DST-1",
  params: { warn_above: 0.1 },
};

/**
 * Serve `pages` in order; the last one repeats for any request past the end. Returns the
 * URL strings so a test can assert exactly what was asked for.
 */
function stubPages(
  pages: { items: ValidationRule[]; next_cursor: string | null }[],
): string[] {
  const calls: string[] = [];
  let index = 0;
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: string | URL) => {
      calls.push(String(input));
      const page = pages[Math.min(index, pages.length - 1)] ?? pages[pages.length - 1];
      index += 1;
      return new Response(JSON.stringify(page), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    }),
  );
  return calls;
}

describe("listRules", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("passes the builtin filter through, and omits it when unset", async () => {
    const calls = stubPages([{ items: [], next_cursor: null }]);
    await listRules({ builtin: true });
    await listRules({ builtin: false });
    await listRules();
    expect(new URL(calls[0]!).searchParams.get("builtin")).toBe("true");
    expect(new URL(calls[1]!).searchParams.get("builtin")).toBe("false");
    expect(new URL(calls[2]!).searchParams.get("builtin")).toBeNull();
    calls.forEach((call) => {
      expect(new URL(call).searchParams.get("limit")).toBe(String(PAGE_SIZE));
    });
  });

  it("gathers every page, and reports when the cap cut the list short", async () => {
    stubPages([
      { items: [RULE], next_cursor: "page-2" },
      { items: [RULE], next_cursor: null },
    ]);
    const gathered = await listRules();
    expect(gathered.items).toHaveLength(2);
    expect(gathered.truncated).toBe(false);

    stubPages(
      Array.from({ length: 5 }, (_, i) => ({
        items: [RULE],
        next_cursor: i < 4 ? `page-${i + 2}` : "still-more",
      })),
    );
    const capped = await listRules();
    expect(capped.items).toHaveLength(5);
    expect(capped.truncated).toBe(true);
  });
});
