import { render, screen, within } from "@testing-library/vue";
import { afterEach, describe, expect, it, vi } from "vitest";

import VersionDetailView from "../VersionDetailView.vue";

/** Shaped on the seeded freMTPL2 v1 as the API returns it. */
const VERSION = {
  id: "01a00495-59db-727d-a33d-33c23e973e13",
  dataset_id: "01a00495-58d0-71f8-a039-cd4c45337960",
  workspace_id: "01a00495-4977-7ec0-95e3-850dc18d1177",
  version: 1,
  status: "validating",
  kind: "ingested",
  totals: {
    exposure_years: "339006.500000",
    claim_count: 36102,
    claim_amount_minor: 407540056,
  },
  tables: [
    {
      name: "policy_exposure",
      record_grain: "policy_exposure",
      primary_key: ["policy_id"],
      row_count: 678013,
      blob: { sha256: "a".repeat(64), bytes: 20387600, media_type: "application/vnd.apache.parquet" },
      arrow_schema: { policy_id: "String", exposure_years: "Float64" },
      source_names: { policy_id: "IDpol", exposure_years: "Exposure" },
    },
  ],
  library_versions: {},
  created_at: "2026-08-15T09:00:00Z",
};

const REJECTED = {
  rows_read: 678013,
  rows_written: 678013,
  rows_rejected: 0,
  reject_rate: 0,
  sample: [],
};

function stub(rejected: unknown = REJECTED, rejectedStatus = 200): void {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: string | URL) => {
      const url = String(input);
      const body = url.includes("/rejected") ? rejected : VERSION;
      return new Response(JSON.stringify(body), {
        status: url.includes("/rejected") ? rejectedStatus : 200,
        headers: { "Content-Type": "application/json" },
      });
    }),
  );
}

afterEach(() => vi.unstubAllGlobals());

const props = { slug: "fremtpl2", version: "1", currency: "EUR" };
//: `RouterLink: true` renders `<router-link-stub>` and **discards the default slot**, so
//: any assertion on a link's text fails against an empty element.
const mounted = {
  global: { stubs: { RouterLink: { template: "<a><slot /></a>" } } },
};

describe("the version detail view", () => {
  it("shows exposure exactly as the backend summed it", async () => {
    stub();
    render(VersionDetailView, { props, ...mounted });
    // 339006.5, not 339006.49999999994 — formatted from the string, never parsed.
    expect(await screen.findByText(/339,006\.5/)).toBeInTheDocument();
  });

  it("shows incurred in the dataset's currency", async () => {
    stub();
    render(VersionDetailView, { props, ...mounted });
    // €4,075,400.56 from 407540056 minor units — a French book, not a British one.
    expect(await screen.findByText(/4,075,400\.56/)).toBeInTheDocument();
  });

  it("shows the source header each column came from", async () => {
    // FR-DATA-5. `IDpol` normalises to `i_dpol`, and without the original a user cannot
    // tell which of their columns a rule is talking about.
    stub();
    render(VersionDetailView, { props, ...mounted });
    const schema = await screen.findByRole("table");
    expect(within(schema).getByText("IDpol")).toBeInTheDocument();
    expect(within(schema).getByText("Exposure")).toBeInTheDocument();
  });

  it("reports a clean ingestion rather than an empty drawer", async () => {
    stub();
    render(VersionDetailView, { props, ...mounted });
    expect(await screen.findByText(/Every row was accepted/)).toBeInTheDocument();
  });

  it("offers the factor workbench only once the version is validated", async () => {
    // `02` R1: a banding is proposed against a `validated` version and nothing else, so a
    // link on a `validating` one would send the actuary to a 409 the screen cannot explain.
    stub();
    render(VersionDetailView, { props, ...mounted });
    expect(await screen.findByText(/Every row was accepted/)).toBeInTheDocument();
    expect(screen.queryByText("Factor workbench")).not.toBeInTheDocument();
  });

  it("links to the workbench by version id, which is what its route takes", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: string | URL) => {
        const url = String(input);
        const body = url.includes("/rejected")
          ? REJECTED
          : { ...VERSION, status: "validated" };
        return new Response(JSON.stringify(body), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }),
    );
    render(VersionDetailView, { props, ...mounted });
    const link = await screen.findByText("Factor workbench");
    expect(link.closest("a")!.getAttribute("to")).toBe(`/factors/${VERSION.id}`);
  });

  it("links the wf-01 A9 profile for a version at any status", async () => {
    // FR-OVR-22: the profile screen was built but nothing reached it. It is a
    // version-level surface like the validation report, not gated on `validated`.
    stub();
    render(VersionDetailView, { props, ...mounted });
    const link = await screen.findByText("Profile");
    expect(link.closest("a")!.getAttribute("to")).toBe(
      `/data/${props.slug}/v/${VERSION.version}/profile`,
    );
  });

  it("treats a version with no ingestion run as an answer, not an error", async () => {
    // A derived version has no run of its own. FR-DATA-7's 404 here is ordinary.
    stub(
      { title: "This version has no ingestion run", status: 404, code: "NOT_FOUND", errors: [] },
      404,
    );
    render(VersionDetailView, { props, ...mounted });
    expect(await screen.findByText(/derived from another/)).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
});
