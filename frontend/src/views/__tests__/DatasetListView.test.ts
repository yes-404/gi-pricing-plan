import { render, screen, waitFor } from "@testing-library/vue";
import { afterEach, describe, expect, it, vi } from "vitest";

import DatasetListView from "../DatasetListView.vue";

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
      created_at: "2026-08-15T08:30:00Z",
    },
  ],
  next_cursor: null,
  total_estimate: 1,
};

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
    stubFetch(200, SEEDED);
    render(DatasetListView);

    expect(await screen.findByText("freMTPL2 — French motor TPL")).toBeInTheDocument();
    expect(screen.getByText("fremtpl2-a78676")).toBeInTheDocument();
    expect(screen.getByText("EUR")).toBeInTheDocument();
    expect(screen.getByText("v2")).toBeInTheDocument();
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
