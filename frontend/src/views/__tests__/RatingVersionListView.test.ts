import { fireEvent, render, screen, within } from "@testing-library/vue";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { components } from "@/api/generated/schema";
import RatingVersionListView from "../RatingVersionListView.vue";

type RatingVersion = components["schemas"]["RatingVersion"];
type Environment = components["schemas"]["Environment"];

/**
 * The view is exercised through the real `api/` modules with `fetch` stubbed, not through a
 * mocked `api/environments`: cases (c) and (d) are about the paging and the failure path
 * (FR-8209), which a mocked client would skip.
 */

function rating(over: Partial<RatingVersion> & Pick<RatingVersion, "slug" | "version" | "status">): RatingVersion {
  return {
    id: `01a04394-0000-7000-8000-${String(over.version).padStart(12, "0")}`,
    workspace_id: "01a04394-0000-7000-8000-000000000001",
    dataset_version_id: "01a04394-0000-7000-8000-000000000002",
    model_ref: "model:fremtpl2-glm-7edfde@1",
    created_at: "2026-08-27T14:00:00Z",
    created_by: "01a04394-0000-7000-8000-000000000003",
    updated_at: "2026-08-27T14:05:00Z",
    ...over,
  };
}

function environment(slug: string, live: string[]): Environment {
  return {
    slug,
    name: slug.toUpperCase(),
    promotion_order: 1,
    live_deployments: live.map((ref) => ({
      rating_version_ref: ref,
      deployed_at: "2026-09-01T09:00:00Z",
      bundle_hash: `sha256:${"a".repeat(64)}`,
    })),
  } as Environment;
}

const VERSIONS: RatingVersion[] = [
  rating({
    slug: "motor-gb", version: 27, status: "live",
    effective_from: "2026-01-01T00:00:00Z", effective_to: "2026-12-31T00:00:00Z",
  }),
  rating({ slug: "fremtpl2-demo", version: 1, status: "approved" }),
  rating({
    slug: "fremtpl2-demo", version: 2, status: "draft",
    pins: { rate_tables: ["rate_table:area@3", "rate_table:band@2"] },
  } as Partial<RatingVersion> & Pick<RatingVersion, "slug" | "version" | "status">),
];

interface Stub {
  versions?: RatingVersion[] | Response;
  /** one entry per environments page, in order; a Response is returned as it is. */
  environmentPages?: ({ items: Environment[]; next_cursor: string | null } | Response)[];
  /** keep returning a next cursor, so the paging helper stops at its cap. */
  endless?: boolean;
}

function problem(status: number, code: string): Response {
  return new Response(
    JSON.stringify({
      type: "about:blank", title: "Refused", status, code, errors: [], trace_id: "abc123",
    }),
    { status, headers: { "Content-Type": "application/problem+json" } },
  );
}

function json(body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status: 200, headers: { "Content-Type": "application/json" },
  });
}

function stubFetch(stub: Stub) {
  let envCall = 0;
  const calls: URL[] = [];
  const fetch = vi.fn(async (input: unknown) => {
    const url = new URL(String(input), "http://localhost");
    calls.push(url);
    if (url.pathname === "/api/v1/rating-versions") {
      const versions = stub.versions ?? VERSIONS;
      return versions instanceof Response ? versions : json(versions);
    }
    if (url.pathname === "/api/v1/environments") {
      const pages = stub.environmentPages ?? [{ items: [], next_cursor: null }];
      const page = pages[Math.min(envCall, pages.length - 1)]!;
      envCall += 1;
      if (page instanceof Response) return page;
      return json({
        ...page,
        next_cursor: stub.endless ? "more" : page.next_cursor,
        total_estimate: 0,
      });
    }
    throw new Error(`unexpected request: ${url.pathname}`);
  });
  vi.stubGlobal("fetch", fetch);
  return { fetch, calls };
}

const mounted = {
  global: {
    stubs: { RouterLink: { props: ["to"], template: "<a :href=\"to\"><slot /></a>" } },
  },
};

/** The row of one version: the table row holding its `slug@version` text. */
async function rowOf(slug: string, version: number) {
  const row = (await screen.findByText(`${slug}@${version}`)).closest("tr");
  if (!row) throw new Error(`no row for ${slug}@${version}`);
  return row;
}

afterEach(() => vi.unstubAllGlobals());

describe("the rating version list view (FR-8209)", () => {
  it("(a) groups the versions by slug, newest version first, and filters by status", async () => {
    stubFetch({});
    render(RatingVersionListView, mounted);

    const headings = await screen.findAllByRole("heading", { level: 2 });
    expect(headings.map((h) => h.textContent?.trim())).toEqual(["fremtpl2-demo", "motor-gb"]);
    const refs = screen.getAllByText(/^(fremtpl2-demo|motor-gb)@\d+$/).map((e) => e.textContent);
    expect(refs).toEqual(["fremtpl2-demo@2", "fremtpl2-demo@1", "motor-gb@27"]);

    await fireEvent.update(screen.getByLabelText("Status"), "draft");

    expect(screen.getByText("fremtpl2-demo@2")).toBeInTheDocument();
    expect(screen.queryByText("fremtpl2-demo@1")).not.toBeInTheDocument();
    expect(screen.queryByText("motor-gb@27")).not.toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "motor-gb" })).not.toBeInTheDocument();
  });

  it("(b) badges a version with the environment it is live in, and only that one", async () => {
    stubFetch({
      environmentPages: [{
        items: [
          environment("dev", ["rating_version:fremtpl2-demo@2"]),
          environment("uat", ["rating_version:motor-gb@27"]),
        ],
        next_cursor: null,
      }],
    });
    render(RatingVersionListView, mounted);

    const live = await rowOf("motor-gb", 27);
    expect(within(live).getByText("uat")).toBeInTheDocument();
    expect(within(live).queryByText("dev")).not.toBeInTheDocument();
    const other = await rowOf("fremtpl2-demo", 1);
    expect(within(other).queryByText("dev")).not.toBeInTheDocument();
    expect(within(other).queryByText("uat")).not.toBeInTheDocument();
    expect(within(other).queryByText("unavailable")).not.toBeInTheDocument();
  });

  it("(b) shows every environment a version is live in", async () => {
    stubFetch({
      environmentPages: [{
        items: [
          environment("uat", ["rating_version:motor-gb@27"]),
          environment("prod", ["rating_version:motor-gb@27"]),
        ],
        next_cursor: null,
      }],
    });
    render(RatingVersionListView, mounted);

    const row = await rowOf("motor-gb", 27);
    expect(within(row).getByText("uat")).toBeInTheDocument();
    expect(within(row).getByText("prod")).toBeInTheDocument();
  });

  it("(c) reads every page of the environments: a badge from page 2 is shown", async () => {
    const { calls } = stubFetch({
      environmentPages: [
        { items: [environment("dev", [])], next_cursor: "page-2" },
        { items: [environment("uat", ["rating_version:motor-gb@27"])], next_cursor: null },
      ],
    });
    render(RatingVersionListView, mounted);

    const row = await rowOf("motor-gb", 27);
    expect(await within(row).findByText("uat")).toBeInTheDocument();
    const envCalls = calls.filter((u) => u.pathname === "/api/v1/environments");
    expect(envCalls).toHaveLength(2);
    expect(envCalls[1]!.searchParams.get("cursor")).toBe("page-2");
  });

  it("(d) a 403 on the environments reads \"unavailable\" on every row, never \"not live\"", async () => {
    stubFetch({ environmentPages: [problem(403, "FORBIDDEN")] });
    render(RatingVersionListView, mounted);

    await rowOf("motor-gb", 27);
    expect(await screen.findAllByText("unavailable")).toHaveLength(VERSIONS.length);
    expect(screen.queryByText(/not live/i)).not.toBeInTheDocument();
  });

  it("(d) a failing second page voids the badges of every row: no partial set", async () => {
    stubFetch({
      environmentPages: [
        { items: [environment("uat", ["rating_version:motor-gb@27"])], next_cursor: "page-2" },
        problem(500, "INTERNAL"),
      ],
    });
    render(RatingVersionListView, mounted);

    await rowOf("motor-gb", 27);
    expect(await screen.findAllByText("unavailable")).toHaveLength(VERSIONS.length);
    expect(screen.queryByText("uat")).not.toBeInTheDocument();
    expect(screen.queryByText(/not live/i)).not.toBeInTheDocument();
  });

  it("(d) a read that stops at the page cap is unavailable, not a short live set", async () => {
    stubFetch({
      endless: true,
      environmentPages: [{ items: [environment("uat", ["rating_version:motor-gb@27"])], next_cursor: "more" }],
    });
    render(RatingVersionListView, mounted);

    await rowOf("motor-gb", 27);
    expect(await screen.findAllByText("unavailable")).toHaveLength(VERSIONS.length);
    expect(screen.queryByText("uat")).not.toBeInTheDocument();
  });

  it("(e) renders effective_from and effective_to as dates (FR-241)", async () => {
    stubFetch({});
    render(RatingVersionListView, mounted);

    const row = await rowOf("motor-gb", 27);
    expect(within(row).getByText("2026-01-01")).toBeInTheDocument();
    expect(within(row).getByText("2026-12-31")).toBeInTheDocument();
  });

  it("(f) links each row by its own slug@version, with no second lookup (FR-1531)", async () => {
    const { calls } = stubFetch({});
    render(RatingVersionListView, mounted);

    const row = await rowOf("fremtpl2-demo", 2);
    const href = (name: string) => within(row).getByRole("link", { name }).getAttribute("href");
    expect(href("Design")).toBe("/rating/fremtpl2-demo/v/2/design");
    expect(href("Sandbox")).toBe("/rating/fremtpl2-demo/v/2/sandbox");
    expect(href("Dislocation")).toBe("/rating/fremtpl2-demo/v/2/dislocation");
    expect(href("area@3")).toBe("/rating/fremtpl2-demo/v/2/tables/area");
    expect(href("band@2")).toBe("/rating/fremtpl2-demo/v/2/tables/band");

    const none = await rowOf("fremtpl2-demo", 1);
    expect(within(none).queryByRole("link", { name: /@\d+$/ })).not.toBeInTheDocument();
    // one list read and the environments read; nothing addressed by id or by slug@version.
    expect(new Set(calls.map((u) => u.pathname))).toEqual(
      new Set(["/api/v1/rating-versions", "/api/v1/environments"]),
    );
  });

  it("renders a failed list read as an alert, not an empty list", async () => {
    stubFetch({ versions: problem(403, "FORBIDDEN") });
    render(RatingVersionListView, mounted);

    expect(await screen.findByRole("alert")).toHaveTextContent("Refused");
    expect(screen.queryByRole("row")).not.toBeInTheDocument();
  });
});
