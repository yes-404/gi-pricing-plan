import { describe, expect, it, vi, beforeEach } from "vitest";

import { listPerilStructures, PERIL_STRUCTURE_PAGE_CAP } from "../perils";
import * as paging from "../paging";

describe("listPerilStructures", () => {
  beforeEach(() => vi.restoreAllMocks());

  it("passes both of FR-167's filters through, and no others", async () => {
    const spy = vi.spyOn(paging, "pageThrough").mockResolvedValue({ items: [], truncated: false });
    await listPerilStructures({ status: "reconciled", slug: "motor-2026" });
    expect(spy).toHaveBeenCalledWith(
      "/peril-structures",
      { status: "reconciled", slug: "motor-2026" },
      PERIL_STRUCTURE_PAGE_CAP,
    );
  });

  it("caps the sweep and reports truncation rather than logging it", async () => {
    vi.spyOn(paging, "pageThrough").mockResolvedValue({ items: [], truncated: true });
    const page = await listPerilStructures({});
    expect(page.truncated).toBe(true);
  });

  it("sends no filter it was not given", async () => {
    // `pageThrough` drops an `undefined` out of the query string rather than sending an empty
    // value, so an unset filter must arrive as `undefined` and not as "".
    const spy = vi.spyOn(paging, "pageThrough").mockResolvedValue({ items: [], truncated: false });
    await listPerilStructures({});
    expect(spy).toHaveBeenCalledWith(
      "/peril-structures",
      { status: undefined, slug: undefined },
      PERIL_STRUCTURE_PAGE_CAP,
    );
  });
});
