import { render, screen, within } from "@testing-library/vue";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { OneWaySummary, Profile } from "@/api/profiles";

import ProfileView from "../ProfileView.vue";

vi.mock("@/components/OneWayChart.vue", () => ({
  // ECharts needs a real canvas. The chart's own behaviour is tested separately; here it
  // would only prove happy-dom cannot measure a container.
  default: { name: "OneWayChart", props: ["summary"], template: "<div data-testid='chart' />" },
}));

vi.mock("@/components/HistogramChart.vue", () => ({
  default: {
    name: "HistogramChart",
    props: ["histogram"],
    template: "<div data-testid='histogram' />",
  },
}));

/**
 * Shaped on freMTPL2 v2 as the API returns it.
 *
 * Annotated with the generated types rather than left a bare literal: the fixtures are
 * then bound to the contract, and a `model-schema` rename — FR-DATA-46's was the last one
 * — fails `type-check` here instead of leaving a test that passes against a shape the API
 * no longer sends.
 */
const PROFILE: Profile = {
  id: "11111111-1111-4111-8111-111111111111",
  dataset_version_id: "22222222-2222-4222-8222-222222222222",
  computed_at: "2026-08-15T11:00:00Z",
  row_count: 29970,
  weight_column: "exposure_years",
  library_versions: {},
  columns: [
    {
      name: "veh_brand", dtype: "String", semantic_type: "categorical", row_count: 29970,
      null_count: 0, null_rate: 0, distinct_count: 11, quantiles: {},
      top_levels: [["B12", 8000], ["B1", 5000]],
    },
    {
      name: "driv_age", dtype: "Int64", semantic_type: "continuous", row_count: 29970,
      null_count: 0, null_rate: 0, distinct_count: 82, mean: 45.2, minimum: 18,
      maximum: 99, std: 14.1, quantiles: {}, top_levels: [],
      // FR-DATA-48: continuous columns carry one, categorical columns do not.
      histogram: { edges: [18, 58, 99], counts: [17000, 12970], exposure: ["8100.5", "6200.25"] },
    },
  ],
  one_ways: [
    { column: "veh_brand", banding: "levels", rows: [] },
    { column: "region", banding: "levels", rows: [] },
  ],
};

const ONE_WAY: OneWaySummary = {
  column: "veh_brand",
  banding: "levels",
  rows: [
    {
      level: "B12",
      exposure_years: "2722.242517",
      claim_count: 378,
      claim_amount_minor: 26758000,
      frequency: 0.138859,
      frequency_ci: [0.1253, 0.1534],
      mean_severity: 70788.36,
      severity_ci: null,
      mean_burning_cost: 9829.44,
    },
  ],
};

const VERSION = { id: PROFILE.dataset_version_id, version: 2 };

function stub(oneWayStatus = 200, oneWayBody: unknown = ONE_WAY): void {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: string | URL) => {
      const url = String(input);
      if (url.includes("/one-ways")) {
        return new Response(JSON.stringify(oneWayBody), {
          status: oneWayStatus,
          headers: { "Content-Type": "application/json" },
        });
      }
      const body = url.includes("/profile") ? PROFILE : VERSION;
      return new Response(JSON.stringify(body), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    }),
  );
}

beforeEach(() => stub());
afterEach(() => vi.unstubAllGlobals());

const props = { slug: "fremtpl2", version: "2", currency: "EUR" };
//: `RouterLink: true` renders `<router-link-stub>` and **discards the default slot**, so
//: any assertion on a link's text fails against an empty element. This stub keeps the
//: content, which is what the view actually renders.
const mounted = {
  global: { stubs: { RouterLink: { template: "<a><slot /></a>" } } },
};

describe("the profile view", () => {
  it("offers exactly the columns that have a stored one-way", async () => {
    // FR-DATA-26's candidate rating columns. Offering a column with no stored one-way
    // would invite a 404 the user cannot act on.
    render(ProfileView, { props, ...mounted });
    const select = await screen.findByLabelText("Rating factor");
    const options = within(select).getAllByRole("option").map((o) => o.textContent?.trim());
    expect(options).toEqual(["veh_brand", "region"]);
  });

  it("shows incurred as currency and the two ratios as statistics", async () => {
    render(ProfileView, { props, ...mounted });
    const table = await screen.findByRole("table");

    // `claim_amount_minor` is the one exact amount on the row: 26 758 000 cents.
    expect(within(table).getByText(/267,580\.00/)).toBeInTheDocument();
    // `mean_severity` and `mean_burning_cost` are float **ratios** — amount ÷ claims and
    // amount ÷ exposure. Rendering them as currency would imply an exactness they do not
    // have, so they appear as plain statistics.
    expect(within(table).getByText("707.88")).toBeInTheDocument();
    expect(within(table).getByText("98.29")).toBeInTheDocument();
    expect(within(table).queryByText(/€707\.88/)).not.toBeInTheDocument();
  });

  it("shows exposure exactly as stored, without parsing it", async () => {
    render(ProfileView, { props, ...mounted });
    const table = await screen.findByRole("table");
    expect(within(table).getByText("2,722.24")).toBeInTheDocument();
  });

  it("treats a column with no stored one-way as an answer", async () => {
    // FR-DATA-27: the platform refuses to compute one on request, because a fallback
    // would meet NFR-DATA-4's budget in testing and miss it in production.
    stub(404, { title: "No stored one-way", status: 404, code: "NOT_FOUND", errors: [] });
    render(ProfileView, { props, ...mounted });
    const select = await screen.findByLabelText("Rating factor");
    await userEvent.selectOptions(select, "region");
    expect(await screen.findByText(/never computes one on request/)).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("renders a histogram for the column that has one and none for the column that does not", async () => {
    // `01` §5.3 asks the Profile view for histograms. FR-DATA-48 only produces one for a
    // continuous column, so a card per column would be a chart of nothing for the rest.
    render(ProfileView, { props, ...mounted });
    await screen.findByText(/29,970 rows/);

    const histograms = screen.getAllByTestId("histogram");
    expect(histograms).toHaveLength(1);
    expect(histograms[0]?.closest("article")).toHaveTextContent("driv_age");
  });

  it("does not colour the dtype label as though it were a PSI band", async () => {
    // A regression guard rather than a failing test: `psiBand(null)` already resolved to
    // the neutral tone, so the pixels never differed. What was wrong was the claim — the
    // view has no comparison to band, and the selector that will is a later slice.
    const { container } = render(ProfileView, { props, ...mounted });
    await screen.findByText(/29,970 rows/);

    expect(container.innerHTML).not.toContain("text-amber-700");
    expect(container.innerHTML).not.toContain("text-red-700");
    expect(container.innerHTML).not.toContain("psi-");
  });

  it("summarises what the profile covers", async () => {
    render(ProfileView, { props, ...mounted });
    expect(await screen.findByText(/29,970 rows/)).toBeInTheDocument();
    expect(screen.getByText(/2 candidate rating factors/)).toBeInTheDocument();
  });
});
