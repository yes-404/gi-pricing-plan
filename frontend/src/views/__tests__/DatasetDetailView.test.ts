import userEvent from "@testing-library/user-event";
import { render, screen, waitFor, within } from "@testing-library/vue";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import DatasetDetailView from "../DatasetDetailView.vue";

const DATASET = {
  id: "11111111-1111-4111-8111-111111111111",
  workspace_id: "22222222-2222-4222-8222-222222222222",
  slug: "fremtpl2-bf4c58",
  name: "freMTPL2 — French motor TPL",
  line_of_business: "motor",
  territory: "FR",
  currency: "EUR",
  validation_rule_set_id: "33333333-3333-4333-8333-333333333333",
  latest_version: 2,
  created_at: "2026-08-15T11:00:00Z",
  data_dictionary: {
    policy_id: { description: "Policy key", semantic_type: "identifier", pii_class: "pseudonymous_key" },
    date_of_birth: { description: "DOB", pii_class: "direct_identifier" },
    veh_brand: { description: "Vehicle brand group", semantic_type: "categorical", pii_class: "none" },
  },
};

const VERSIONS = {
  items: [
    { id: "a", dataset_id: DATASET.id, workspace_id: DATASET.workspace_id, version: 2,
      status: "validated", kind: "ingested", tables: [], library_versions: {},
      validation_report_id: "r", totals: { exposure_years: "15974.643626", claim_count: 1639, claim_amount_minor: 203893993 },
      created_at: "2026-08-15T11:05:00Z" },
    { id: "b", dataset_id: DATASET.id, workspace_id: DATASET.workspace_id, version: 1,
      status: "validating", kind: "ingested", tables: [], library_versions: {},
      created_at: "2026-08-15T11:00:00Z" },
  ],
  next_cursor: null,
  total_estimate: 2,
};

function stub(putStatus = 200): void {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: string | URL, init?: RequestInit) => {
      const url = String(input);
      if (init?.method === "PUT") {
        const body = putStatus === 200
          ? { ...DATASET, data_dictionary: JSON.parse(String(init.body)).data_dictionary }
          : { title: "Not permitted", status: 403, code: "PERMISSION_DENIED", errors: [] };
        return new Response(JSON.stringify(body), {
          status: putStatus, headers: { "Content-Type": "application/json" },
        });
      }
      const body = url.includes("/versions") ? VERSIONS : DATASET;
      return new Response(JSON.stringify(body), {
        status: 200, headers: { "Content-Type": "application/json" },
      });
    }),
  );
}

beforeEach(() => stub());
afterEach(() => vi.unstubAllGlobals());

const props = { slug: "fremtpl2-bf4c58" };
//: `RouterLink: true` renders `<router-link-stub>` and **discards the default slot**, so
//: any assertion on a link's text fails against an empty element. This stub keeps the
//: content, which is what the view actually renders.
const mounted = {
  global: { stubs: { RouterLink: { template: "<a><slot /></a>" } } },
};

describe("the dataset detail view", () => {
  it("shows the version timeline newest first", async () => {
    render(DatasetDetailView, { props, ...mounted });
    // The table renders as soon as the *dataset* resolves, which is before the versions
    // do — so waiting for the table alone asserts against an empty one.
    const table = await screen.findByRole("table", { name: "Versions" });
    await waitFor(() => expect(within(table).getAllByRole("row")).toHaveLength(3));

    const rows = within(table).getAllByRole("row").slice(1);
    expect(rows[0]).toHaveTextContent("v2");
    expect(rows[0]).toHaveTextContent("validated");
    expect(rows[1]).toHaveTextContent("v1");
  });

  it("names the columns that may not be modelled on", async () => {
    // FR-OVR-9 refuses `direct_identifier` and `special_category` for modelling. Stating
    // it as a refusal rather than advice, because that is what the platform does.
    render(DatasetDetailView, { props, ...mounted });
    const banner = await screen.findByText(/may not be modelled on/);
    expect(banner).toHaveTextContent("date_of_birth");
    expect(banner).not.toHaveTextContent("veh_brand");
  });

  it("sends the whole dictionary on save, not a patch", async () => {
    // A **replace**: the dictionary decides which columns may be modelled at all, so a
    // removal must be distinguishable from an omission.
    const user = userEvent.setup();
    render(DatasetDetailView, { props, ...mounted });
    await user.click(await screen.findByRole("button", { name: "Edit" }));
    await user.clear(screen.getByLabelText("Description for veh_brand"));
    await user.type(screen.getByLabelText("Description for veh_brand"), "ABI group");
    await user.click(screen.getByRole("button", { name: "Save dictionary" }));

    await waitFor(() => {
      const put = vi.mocked(fetch).mock.calls.find(
        ([, init]) => (init as RequestInit | undefined)?.method === "PUT",
      );
      expect(put).toBeDefined();
      const sent = JSON.parse(String((put as [unknown, RequestInit])[1].body));
      expect(Object.keys(sent.data_dictionary).sort()).toEqual(
        ["date_of_birth", "policy_id", "veh_brand"],
      );
      expect(sent.data_dictionary.veh_brand.description).toBe("ABI group");
    });
  });

  it("does not mutate the displayed dictionary when an edit is cancelled", async () => {
    const user = userEvent.setup();
    render(DatasetDetailView, { props, ...mounted });
    await user.click(await screen.findByRole("button", { name: "Edit" }));
    await user.clear(screen.getByLabelText("Description for veh_brand"));
    await user.type(screen.getByLabelText("Description for veh_brand"), "changed");
    await user.click(screen.getByRole("button", { name: "Cancel" }));

    // The draft is a deep copy; a shallow one would leave the abandoned edit on screen.
    expect(screen.getByText("Vehicle brand group")).toBeInTheDocument();
    expect(screen.queryByText("changed")).not.toBeInTheDocument();
  });

  it("shows the platform's refusal when the save is not permitted", async () => {
    stub(403);
    const user = userEvent.setup();
    render(DatasetDetailView, { props, ...mounted });
    await user.click(await screen.findByRole("button", { name: "Edit" }));
    await user.click(screen.getByRole("button", { name: "Save dictionary" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Not permitted");
  });
});
