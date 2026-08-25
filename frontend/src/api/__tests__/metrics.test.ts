import { describe, expect, it, vi, beforeEach } from "vitest";

import { listMetrics, METRIC_PAGE_CAP } from "../metrics";
import * as paging from "../paging";

describe("listMetrics", () => {
  beforeEach(() => vi.restoreAllMocks());

  it("pages through /custom-metrics under the shared cap", async () => {
    const spy = vi.spyOn(paging, "pageThrough").mockResolvedValue({ items: [], truncated: false });
    await listMetrics({ status: "certified" });
    expect(spy).toHaveBeenCalledWith("/custom-metrics", { status: "certified" }, METRIC_PAGE_CAP);
  });

  it("passes no status when none is asked for", async () => {
    const spy = vi.spyOn(paging, "pageThrough").mockResolvedValue({ items: [], truncated: false });
    await listMetrics();
    expect(spy).toHaveBeenCalledWith("/custom-metrics", { status: undefined }, METRIC_PAGE_CAP);
  });
});
