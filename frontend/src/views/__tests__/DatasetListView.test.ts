import { render, screen, waitFor } from "@testing-library/vue";
import { afterEach, describe, expect, it, vi } from "vitest";

import { cellUnder } from "@/test-tables";

import DatasetListView from "../DatasetListView.vue";

const OWNER = "01a0048c-9f31-70b2-8c4d-6e5b1a2f7d90";

const SEEDED = {
  items: [
    {
      id: "01a0048c-da2f-7513-9de7-0a5e5a9e58cc",
      workspace_id: "01a0048c-766b-73cc-ac8b-af35d55fce8b",
      slug: "fremtpl2-a78676",
      name: "freMTPL2 — French motor TPL",
      line_of_business: "motor",
      territory: "FR",
      currency: "EUR",
      data_dictionary: {},
      latest_version: 2,
      // The three derived fields FR-DATA-50 projects, plus FR-DATA-51's stored owner.
      // Here the latest version *is* the last validated one — Decision 3's agreement
      // branch, where the pair is one fact and no version is named.
      latest_version_status: "validated",
      last_validated_at: "2026-08-20T11:04:00Z",
      last_validated_version: 2,
      owner_id: OWNER,
      created_at: "2026-08-15T08:30:00Z",
    },
  ],
  next_cursor: null,
  total_estimate: 1,
};

/**
 * FR-DATA-50's own worked example: "a Dataset whose v12 is a fresh `draft` above a
 * `validated` v11 would otherwise render as never validated". The badge describes v12; the
 * date describes v11; the requirement says the list must state which.
 */
function disagreeing() {
  return {
    ...SEEDED,
    items: [
      {
        ...SEEDED.items[0],
        latest_version: 12,
        latest_version_status: "draft",
        last_validated_at: "2026-08-20T11:04:00Z",
        last_validated_version: 11,
      },
    ],
  };
}

async function table(body: unknown = SEEDED): Promise<HTMLElement> {
  stubFetch(200, body);
  render(DatasetListView);
  await screen.findByRole("table");
  return screen.getByRole("table");
}

function stubFetch(status: number, body: unknown): void {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () =>
      new Response(JSON.stringify(body), {
        status,
        headers: { "Content-Type": "application/json" },
      }),
    ),
  );
}

afterEach(() => vi.unstubAllGlobals());

describe("the dataset list", () => {
  it("renders what the seeded workspace actually contains", async () => {
    // Read by header rather than by `getByText`. These four assertions used to be bare
    // text lookups, which are safe only while one string of each shape exists in a row.
    // This slice ends that: the last-validated column can render a *second* version
    // number ("v11 · 20/08/2026") beside the latest one, at which point `getByText("v2")`
    // either matches the wrong cell or throws on multiple matches — and in neither case
    // can it say which column it read. Migrated before the columns were added, so these
    // four are proven still passing against the row they were written for.
    const t = await table();

    expect(cellUnder(t, /freMTPL2/, "Name")).toHaveTextContent("freMTPL2 — French motor TPL");
    expect(cellUnder(t, /freMTPL2/, "Name")).toHaveTextContent("fremtpl2-a78676");
    expect(cellUnder(t, /freMTPL2/, "Currency")).toHaveTextContent("EUR");
    expect(cellUnder(t, /freMTPL2/, "Latest version")).toHaveTextContent("v2");
  });

  it("shows the trace id when the request fails", async () => {
    // The trace id is the whole reason for rendering an error rather than a shrug: it
    // turns "it broke" into something an operator can look up.
    stubFetch(403, {
      title: "Not permitted",
      status: 403,
      code: "PERMISSION_DENIED",
      detail: "This action requires dataset:read.",
      errors: [],
      trace_id: "1599f96731df05584ffd3c891439b8e2",
    });
    render(DatasetListView);

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Not permitted");
    expect(alert).toHaveTextContent("1599f96731df05584ffd3c891439b8e2");
  });

  it("says how to get data rather than showing an empty table", async () => {
    stubFetch(200, { items: [], next_cursor: null, total_estimate: 0 });
    render(DatasetListView);
    await waitFor(() =>
      expect(screen.getByText(/seed one with/i)).toBeInTheDocument(),
    );
  });

  it("caps the total rather than reporting an estimate as a count", async () => {
    // `00` §5.2: `total_estimate` is counted up to a cap. Rendering it as an exact total
    // past that point would be a number the platform never claimed.
    stubFetch(200, { ...SEEDED, total_estimate: 1000 });
    render(DatasetListView);
    expect(await screen.findByText(/1,000\+/)).toBeInTheDocument();
  });
});

describe("the three columns W32-3 served and nothing read (FR-DATA-50, FR-DATA-51)", () => {
  it("badges the status of the version `latest_version` names", async () => {
    const t = await table();

    expect(cellUnder(t, /freMTPL2/, "Status")).toHaveTextContent("validated");
  });

  it("does not name the version when it is the latest one", async () => {
    // Decision 3's agreement branch. FR-DATA-50 requires disclosure only "where the two
    // refer to different versions"; here they are one fact and a version number would be
    // noise. Asserted as an absence so the always-name implementation fails here.
    const cell = cellUnder(await table(), /freMTPL2/, "Last validated");

    expect(cell.textContent).not.toMatch(/v\d/);
    expect(cell.textContent?.trim()).not.toBe("—");
  });

  it("names the version when the last validated one is not the latest", async () => {
    // FR-DATA-50's own example, and the branch the requirement was written for: v12 is a
    // fresh draft above a validated v11. The date must not be readable as v12's.
    const t = await table(disagreeing());

    expect(cellUnder(t, /freMTPL2/, "Last validated")).toHaveTextContent("v11");
    expect(cellUnder(t, /freMTPL2/, "Latest version")).toHaveTextContent("v12");
  });

  it("still badges the newest version when the two disagree", async () => {
    // The pair is scoped differently on purpose: the badge answers "what state is the
    // newest version in", not "was this ever validated". A draft above a validated
    // version reads `draft`, and the date beside it is what stops that reading as
    // never-validated.
    const t = await table(disagreeing());

    expect(cellUnder(t, /freMTPL2/, "Status")).toHaveTextContent("draft");
  });

  it("renders a never-validated Dataset with a badge but no date", async () => {
    // The two columns are independently absent: a draft that has never passed validation
    // has a status and no last-validated date.
    const t = await table({
      ...SEEDED,
      items: [{
        ...SEEDED.items[0],
        latest_version: 1,
        latest_version_status: "draft",
        last_validated_at: null,
        last_validated_version: null,
      }],
    });

    expect(cellUnder(t, /freMTPL2/, "Status")).toHaveTextContent("draft");
    expect(cellUnder(t, /freMTPL2/, "Last validated")).toHaveTextContent("—");
  });

  it("shows the whole owner id, not a prefix of it", async () => {
    // Decision 1, as ruled. An opaque id's only utility is exact copy and exact search,
    // and a `String.slice` destroys both — so this asserts the exact value. Narrowing is
    // CSS, which this assertion is blind to and should be.
    const cell = cellUnder(await table(), /freMTPL2/, "Owner");

    expect(cell).toHaveTextContent(OWNER);
    expect(cell.textContent?.trim()).toBe(OWNER);
  });

  it("keeps the owner id in the cell's own text, never only in a title", async () => {
    // WCAG 2.2 SC 1.4.13: a native tooltip is not dismissable, hoverable or persistent,
    // and is unreachable by keyboard and touch. A `title` may be added as a mouse
    // convenience; it may never become the only home of the value. This test fails if a
    // later change moves the id there.
    const cell = cellUnder(await table(), /freMTPL2/, "Owner");

    expect(cell.textContent).toContain(OWNER);
  });

  it("renders different owners differently", async () => {
    // The guard against a hardcoded placeholder, which every single-row test above would
    // otherwise pass.
    const other = "01a0048c-1111-7000-8000-222233334444";
    const t = await table({
      ...SEEDED,
      items: [
        SEEDED.items[0],
        { ...SEEDED.items[0], id: "01a0048c-2222-7000-8000-333344445555",
          slug: "other-ds", name: "Another dataset", owner_id: other },
      ],
    });

    expect(cellUnder(t, /freMTPL2/, "Owner").textContent?.trim()).toBe(OWNER);
    expect(cellUnder(t, /Another dataset/, "Owner").textContent?.trim()).toBe(other);
  });
});
