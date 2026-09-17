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

/** The five-column set the objective and metric libraries declare. */
const ALL_COLUMNS = ["slug", "version", "status", "applicability", "usageCount"] as const;

function table(rows: typeof ROWS | [], truncated: boolean) {
  return render(ArtifactLibraryTable, {
    props: { rows, columns: ALL_COLUMNS, truncated, emptyLabel: "none found" },
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

describe("the column set", () => {
  // A Peril Structure has no `applicability` — FR-153's objective/metric concept — and
  // FR-167 forbids it a usage count.
  const PERIL_COLUMNS = ["slug", "version", "status"] as const;
  // **These rows deliberately CARRY `usageCount` and `applicability`.** With them absent, "no
  // usage column" is satisfied by the value being missing — exactly what a value-driven
  // component would also produce — so the test could not tell the two apart. Carrying values
  // the column set excludes is what proves rendering is driven by `columns`.
  const PERIL_ROWS = [
    {
      id: "p1",
      slug: "motor-2026",
      version: 3,
      status: "reconciled" as const,
      applicability: ["claim_count"],
      usageCount: 7,
      href: "/peril-structures/p1",
    },
  ];

  function perilTable() {
    return render(ArtifactLibraryTable, {
      props: {
        rows: PERIL_ROWS,
        columns: PERIL_COLUMNS,
        truncated: false,
        emptyLabel: "none",
      },
      ...mounted,
    });
  }

  it("omits the usage-count column entirely when it is not in the column set", () => {
    // **Asserted on the header, not on the cell.** A blank cell would pass a naive "no usage
    // count is shown" test while asserting that a count exists and is merely unknown — which
    // is the opposite of what FR-167 says. Absent, not empty.
    const { container } = perilTable();
    const headers = Array.from(container.querySelectorAll("th")).map((h) =>
      (h.textContent ?? "").toLowerCase(),
    );
    expect(headers.some((h) => h.includes("usage") || h.includes("used by"))).toBe(false);
    expect(headers.some((h) => h.includes("applicab"))).toBe(false);
  });

  it("renders one cell per declared column, so no row can be ragged", () => {
    const { container } = perilTable();
    expect(container.querySelectorAll("tbody td")).toHaveLength(PERIL_COLUMNS.length);
  });

  it("still renders both columns for a library that declares them", () => {
    // The control. Without it, the absence assertions above pass just as well against a
    // component that renders neither column for anyone.
    const { container } = table(ROWS, false);
    const headers = Array.from(container.querySelectorAll("th")).map((h) =>
      (h.textContent ?? "").toLowerCase(),
    );
    expect(headers.some((h) => h.includes("used by"))).toBe(true);
    expect(headers.some((h) => h.includes("applicab"))).toBe(true);
  });

  it("renders no usage value even when the row carries one", () => {
    // The behaviour half of the assertion above: not just a missing header, but the value
    // itself nowhere on the page. FR-167 gives a Peril Structure no usage count, so a
    // row that somehow carries one must not surface it.
    const { container } = perilTable();
    expect(container.textContent ?? "").not.toContain("7");
    expect(container.textContent ?? "").not.toContain("claim_count");

    // And not as a defaulted zero. The house idiom is `usage_count ?? 0`, so a count that is
    // absent renders as a literal `0` — which "does not contain 7" passes, because 0 is not
    // 7. A zero usage count is a claim about usage; no column is the absence of the claim.
    const cells = Array.from(container.querySelectorAll("tbody td")).map((c) =>
      (c.textContent ?? "").trim(),
    );
    expect(cells).not.toContain("0");
  });
});
