import { render, screen } from "@testing-library/vue";
import { afterEach, describe, expect, it, vi } from "vitest";

import * as api from "@/api/perils";
import PerilStructureLibraryView from "../PerilStructureLibraryView.vue";

// Contract-shaped: `PerilStructure` requires id/slug/version/perils/created_at, and `status`
// carries a default but is not required.
const STRUCTURE = {
  id: "p1",
  slug: "motor-2026",
  version: 3,
  status: "reconciled",
  perils: [],
  created_at: "2026-07-01T09:30:00Z",
} as unknown as api.PerilStructure;

// A real RouterLink stub that keeps `to` as an href, so the link assertion is about the link
// and not about the stub.
const mounted = {
  global: {
    stubs: { RouterLink: { props: ["to"], template: "<a :href='to'><slot /></a>" } },
  },
};

afterEach(() => vi.restoreAllMocks());

describe("PerilStructureLibraryView", () => {
  it("renders slug, version and status, and never a usage column", async () => {
    vi.spyOn(api, "listPerilStructures").mockResolvedValue({
      items: [STRUCTURE],
      truncated: false,
    });
    const { container } = render(PerilStructureLibraryView, mounted);

    expect(await screen.findByText("motor-2026")).toBeInTheDocument();
    const headers = Array.from(container.querySelectorAll("th")).map((h) =>
      (h.textContent ?? "").toLowerCase(),
    );
    // FR-167 gives a Peril Structure no usage count, and FR-153's applicability is
    // not its concept. Absent, not blank — asserted on the header.
    expect(headers.some((h) => h.includes("usage") || h.includes("used by"))).toBe(false);
    expect(headers.some((h) => h.includes("applicab"))).toBe(false);
    expect(headers).toEqual(["slug", "version", "status"]);

    // Not a defaulted zero either: `usage_count ?? 0` is the idiom the other two libraries
    // use, and copied here it would render `0` in a column FR-167 says cannot exist.
    const cells = Array.from(container.querySelectorAll("tbody td")).map((c) =>
      (c.textContent ?? "").trim(),
    );
    expect(cells).toHaveLength(3);
    expect(cells).not.toContain("0");
  });

  it("links each row into the detail view", async () => {
    // `:2595`'s own words — "each row linking into the per-structure detail view below" — and
    // why this slice cannot ship the library alone.
    vi.spyOn(api, "listPerilStructures").mockResolvedValue({
      items: [STRUCTURE],
      truncated: false,
    });
    const { container } = render(PerilStructureLibraryView, mounted);

    await screen.findByText("motor-2026");
    expect(container.querySelector("a[href='/peril-structures/p1']")).not.toBeNull();
  });

  it("does not call the library empty when the sweep was truncated", async () => {
    vi.spyOn(api, "listPerilStructures").mockResolvedValue({ items: [], truncated: true });
    const { container } = render(PerilStructureLibraryView, mounted);

    await screen.findByText(/More exist/i);
    expect(container.textContent ?? "").not.toContain("No peril structures");
  });
});
