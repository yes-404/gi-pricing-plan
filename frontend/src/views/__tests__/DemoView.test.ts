import { render, screen, within } from "@testing-library/vue";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import DemoView from "../DemoView.vue";

const GUIDE = {
  generated_from: ["docs/specs/*.md §5.3", "frontend/src/router/index.ts"],
  views: [
    {
      spec: "01-data-management", module: "DATA", name: "Dataset list", route: "/data",
      contents: "Datasets with status", implemented: true,
    },
    {
      spec: "01-data-management", module: "DATA", name: "Validation report",
      route: "/data/:slug/v/:version/validation", contents: "The banner", implemented: true,
    },
    {
      spec: "02-modelling", module: "MODEL", name: "Factor workbench",
      route: "/factors/:datasetVersionId", contents: "Banding editor", implemented: false,
    },
  ],
  api: [{ tag: "datasets", endpoints: ["GET /api/v1/datasets", "POST /api/v1/datasets"] }],
  workstreams: [
    { phase: "Phase 1a", workstream: "W4", scope: "Data", status: "✔ closed 2026-08-15",
      closed: true },
    { phase: "Phase 1a", workstream: "W6b", scope: "Frontend platform", status: "next",
      closed: false },
  ],
};

function stub(body: unknown = GUIDE, status = 200): void {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () =>
      new Response(JSON.stringify(body), {
        status, headers: { "Content-Type": "application/json" },
      }),
    ),
  );
}

beforeEach(() => stub());
afterEach(() => vi.unstubAllGlobals());

//: The stub needs `:href` as well as the slot — an `<a>` with no href has no `link`
//: role, so `getAllByRole("link")` finds nothing and the assertion passes for the wrong
//: reason by never running.
const mounted = {
  global: {
    stubs: { RouterLink: { props: ["to"], template: "<a :href=\"to\"><slot /></a>" } },
  },
};

describe("the demo entrance", () => {
  it("names what is not yet functional, not only what is", async () => {
    // The valuable half. A page showing only what works invites the reader to assume
    // everything else works too.
    render(DemoView, mounted);
    const modelling = await screen.findByRole("table", { name: "MODEL views" });
    expect(within(modelling).getByText("not yet")).toBeInTheDocument();
    expect(screen.getByText("MODEL — 0 of 1 built")).toBeInTheDocument();
  });

  it("links only routes that can be opened without an id", async () => {
    // A link with `:slug` in it 404s, and a dead link on the page whose job is saying what
    // works is worse than no link.
    render(DemoView, mounted);
    const links = await screen.findAllByRole("link");
    const hrefs = links.map((link) => link.getAttribute("href") ?? "");
    expect(hrefs).toContain("/data");
    expect(hrefs.some((href) => href.includes(":"))).toBe(false);
  });

  it("reports workstream state in the roadmap's own words", async () => {
    render(DemoView, mounted);
    expect(await screen.findByText("✔ closed 2026-08-15")).toBeInTheDocument();
    expect(screen.getByText("next")).toBeInTheDocument();
  });

  it("reads a 404 as 'not enabled here', never as a failure", async () => {
    // The entrance exists only where development identity does. Calling that an error
    // would send the reader looking for a bug that is not there.
    stub({ title: "The demo entrance is not enabled", status: 404, code: "NOT_FOUND",
      errors: [] }, 404);
    render(DemoView, mounted);
    expect(await screen.findByText(/only where development identity does/))
      .toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("counts what is built against what the specs declare", async () => {
    render(DemoView, mounted);
    expect(await screen.findByText("Views built")).toBeInTheDocument();
    const built = screen.getByText("Views built").closest("div")!;
    expect(built).toHaveTextContent("2/3");
  });
});
