import { render, screen, waitFor, within } from "@testing-library/vue";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import ReferenceView from "../ReferenceView.vue";

const TABLES = [
  {
    id: "1", slug: "postcode-area", key_columns: ["postcode"], payload_columns: ["area"],
    description: "Postcode to rating area", created_at: "2026-01-01T00:00:00Z",
    latest_published_version: 2, version_count: 2,
  },
  {
    id: "2", slug: "vehicle-group", key_columns: ["abi_code"], payload_columns: ["group"],
    description: null, created_at: "2026-01-01T00:00:00Z",
    latest_published_version: null, version_count: 1,
  },
];

const VERSIONS = [
  {
    id: "v3", slug: "postcode-area", version: 3, status: "draft", source_note: "next year",
    created_at: "2026-08-01T00:00:00Z", row_count: 4,
    covers_from: "2027-01-01", covers_to: "2028-01-01",
  },
  {
    id: "v2", slug: "postcode-area", version: 2, status: "published",
    source_note: "2026 refresh", created_at: "2026-01-01T00:00:00Z", row_count: 3,
    covers_from: "2026-01-01", covers_to: null,
  },
];

const ROWS = [
  { key: "SW1A", payload: { area: 12 }, effective_from: "2026-01-01",
    effective_to: "2026-07-01" },
  { key: "SW1A", payload: { area: 13 }, effective_from: "2026-07-01", effective_to: null },
];

let asked: string[] = [];

function stub(over: { rows?: unknown; lookupStatus?: number; lookupBody?: unknown } = {}): void {
  asked = [];
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: string | URL) => {
      const url = String(input);
      asked.push(url.replace(/^.*\/api\/v1/, ""));
      const json = (body: unknown, status = 200) =>
        new Response(JSON.stringify(body), {
          status, headers: { "Content-Type": "application/json" },
        });

      if (url.includes("/lookup")) {
        return json(
          over.lookupBody ?? {
            reference_table_version_id: "v2", version: 2, key: "SW1A",
            payload: { area: 13 }, effective_from: "2026-07-01", effective_to: null,
          },
          over.lookupStatus ?? 200,
        );
      }
      if (url.includes("/rows")) return json(over.rows ?? ROWS);
      if (url.includes("/versions")) return json(VERSIONS);
      return json(TABLES);
    }),
  );
}

beforeEach(() => stub());
afterEach(() => vi.unstubAllGlobals());

describe("the reference view", () => {
  it("says when a table has no published version, rather than showing a number", async () => {
    // FR-72: rating pins a published version. A table whose versions are all drafts
    // cannot be pinned at all, and a version number here would say it is usable.
    render(ReferenceView);
    const tables = await screen.findByRole("table", { name: "Reference tables" });
    const row = within(tables).getByText("vehicle-group").closest("tr")!;
    expect(within(row).getByText("no published version")).toBeInTheDocument();
  });

  it("opens on the newest published version, not the newest version", async () => {
    // v3 is a draft. Opening on it would show a version no quote can have used.
    render(ReferenceView);
    await waitFor(() => expect(asked.some((u) => u.includes("/rows"))).toBe(true));
    expect(asked.find((u) => u.includes("/rows"))).toContain("/versions/2/rows");
  });

  it("shows an open-ended version as open-ended, not as missing data", async () => {
    render(ReferenceView);
    expect(await screen.findByText(/2026-01-01 → open-ended/)).toBeInTheDocument();
    expect(screen.getByText(/2027-01-01 → 2028-01-01/)).toBeInTheDocument();
  });

  it("labels the end of an interval as exclusive, and open rows as open-ended", async () => {
    // The interval is half-open: a row ending 2026-07-01 does not cover that day. A blank
    // cell would read as unknown, and a plain "to" as inclusive — both mislead a reader
    // checking why a quote changed on the 1st.
    render(ReferenceView);
    const rows = await screen.findByRole("table", { name: "Reference rows" });
    expect(within(rows).getByText("Until (exclusive)")).toBeInTheDocument();
    // Awaited: the table renders before its rows arrive, so a synchronous query here
    // would assert against an empty body and pass for the wrong reason.
    expect(await within(rows).findByText("open-ended")).toBeInTheDocument();
  });

  it("filters the pinned version by date and never selects another one", async () => {
    render(ReferenceView);
    await screen.findByRole("table", { name: "Reference rows" });
    await userEvent.type(screen.getByLabelText("As at"), "2026-06-30");
    await waitFor(() =>
      expect(asked.some((u) => u.includes("as_at=2026-06-30"))).toBe(true));
    // Still v2 — the date is a filter over the pinned version, not a selector across them.
    expect(asked.filter((u) => u.includes("/rows")).every((u) => u.includes("/versions/2/")))
      .toBe(true);
  });

  it("explains a lookup miss in the server's own terms", async () => {
    stub({
      lookupStatus: 404,
      lookupBody: {
        title: "No reference row for that key on that date", status: 404, code: "NOT_FOUND",
        detail: "'postcode-area'@2 has no row for key 'EC1' effective on 2026-09-01. "
          + "The interval is half-open: a row ending on that date does not cover it.",
        errors: [],
      },
    });
    render(ReferenceView);
    await screen.findByRole("table", { name: "Reference rows" });
    await userEvent.type(screen.getByLabelText("As at"), "2026-09-01");
    await userEvent.type(screen.getByLabelText("Key"), "EC1");
    await userEvent.click(screen.getByRole("button", { name: "Look up" }));
    expect(await screen.findByText(/half-open/)).toBeInTheDocument();
  });

  it("refuses to look up without a date, and says why", async () => {
    render(ReferenceView);
    await screen.findByRole("table", { name: "Reference rows" });
    expect(screen.getByRole("button", { name: "Look up" })).toBeDisabled();
    expect(screen.getByText(/a lookup with no date has no answer/)).toBeInTheDocument();
  });
});
