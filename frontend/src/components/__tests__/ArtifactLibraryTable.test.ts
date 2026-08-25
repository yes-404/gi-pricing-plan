import { render, screen } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import ArtifactLibraryTable from "../ArtifactLibraryTable.vue";

// `@testing-library/vue`, not `@vue/test-utils`: the latter is not a dependency of this
// project and no test in `frontend/src` imports it. Adding one would be a `CLAUDE.md` §3
// stack decision, and there is nothing here the house library cannot express.
const ROWS = [
  {
    id: "a",
    slug: "tweedie-cap",
    version: 2,
    status: "approved" as const,
    applicability: ["claim_count"],
    usageCount: 3,
    href: "/objectives/a/certificate",
  },
];

const mounted = { global: { stubs: { RouterLink: { template: "<a><slot /></a>" } } } };

function table(rows: typeof ROWS | [], truncated: boolean) {
  return render(ArtifactLibraryTable, {
    props: { rows, truncated, emptyLabel: "none found" },
    ...mounted,
  });
}

describe("ArtifactLibraryTable", () => {
  it("renders slug, version, applicability and usage count", () => {
    const { container } = table(ROWS, false);
    const text = container.textContent ?? "";
    expect(text).toContain("tweedie-cap");
    expect(text).toContain("claim_count");
    expect(text).toContain("3");
  });

  it("says so when the sweep was truncated", () => {
    const { container } = table(ROWS, true);
    expect((container.textContent ?? "").toLowerCase()).toContain("more");
  });

  it("does not claim an empty library when the sweep was truncated", () => {
    // The one worth writing: an empty page under a truncated sweep is indistinguishable from
    // an empty library, and saying "none found" there is a lie the user cannot detect.
    const { container } = table([], true);
    expect(container.textContent ?? "").not.toContain("none found");
  });

  it("says the library is empty when the sweep was complete", () => {
    // The control for the test above. Without it, "none found is absent" passes just as well
    // when the empty label never renders at all.
    table([], false);
    expect(screen.getByText("none found")).toBeInTheDocument();
  });
});
