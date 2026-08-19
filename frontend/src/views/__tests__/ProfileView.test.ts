import { render, screen, waitFor, within } from "@testing-library/vue";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { OneWaySummary, Profile, ProfileComparison } from "@/api/profiles";

import ProfileView from "../ProfileView.vue";

// The view reads `?against` and writes it back with `router.replace` (OQ-DATA-11). A real
// router would make every test in this file wait on navigation readiness; the mock keeps
// the query controllable and lets one test assert what the view wrote.
const routerReplace = vi.fn();
const routeQuery: { against?: string } = {};
vi.mock("vue-router", async (importOriginal) => ({
  ...(await importOriginal<typeof import("vue-router")>()),
  useRoute: () => ({ query: routeQuery }),
  useRouter: () => ({ replace: routerReplace }),
}));

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
      // Mixing a weighted level (B12), an unweighted one (B1) and a null level within one
      // column is not a shape either profiling engine can produce — both set
      // `exposure_years` uniformly per column: present on every level or absent from all
      // of them. This fixture is deliberately unproducible; it exists only to exercise
      // the chip's three render branches (with exposure, without, null level) in one
      // column instead of three, and must not be read as documenting a real profile.
      top_levels: [
        { level: "B12", count: 8000, exposure_years: "4123.5" },
        { level: "B1", count: 5000, exposure_years: null },
        { level: null, count: 200, exposure_years: "10.5" },
      ],
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

const VERSIONS = {
  items: [
    { id: PROFILE.dataset_version_id, version: 2, profile_id: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa" },
    { id: "33333333-3333-4333-8333-333333333333", version: 1, profile_id: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb" },
    // A version that was ingested but never profiled: the endpoint would 404 for it, so
    // the picker must not offer it as a choice.
    { id: "44444444-4444-4444-8444-444444444444", version: 3, profile_id: null },
  ],
  next_cursor: null,
  total_estimate: 3,
};

const COMPARISON: ProfileComparison = {
  current_version_id: PROFILE.dataset_version_id,
  reference_version_id: "33333333-3333-4333-8333-333333333333",
  row_count_ratio: 1.0203,
  columns: [
    {
      column: "veh_brand",
      psi: 0.31,
      mean_shift: null,
      null_rate_shift: 0.012,
      new_levels: ["B14"],
      vanished_levels: [],
    },
    // Continuous: `compare_profiles` measures PSI from non-null `top_levels`, and this
    // column has none — so `psi` is null and there is no band to draw.
    {
      column: "driv_age",
      psi: null,
      mean_shift: 1.35,
      null_rate_shift: 0,
      new_levels: [],
      vanished_levels: [],
    },
  ],
};

function stub(
  oneWayStatus = 200,
  oneWayBody: unknown = ONE_WAY,
  compare: { status?: number; body?: unknown } = {},
  versions: { status?: number; body?: unknown } = {},
): void {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: string | URL) => {
      const url = String(input);
      const json = (body: unknown, status = 200): Response =>
        new Response(JSON.stringify(body), {
          status,
          headers: { "Content-Type": "application/json" },
        });

      if (url.includes("/one-ways")) return json(oneWayBody, oneWayStatus);
      if (url.includes("/compare")) return json(compare.body ?? COMPARISON, compare.status ?? 200);
      // The versions *list* is `/datasets/{slug}/versions[?query]` — nothing after
      // "versions" but a query string or the end. The single-version lookup
      // `/datasets/{slug}/versions/{number}` also contains "/versions" as a substring, so
      // a plain `.includes("/versions")` would swallow it too; it must stay the
      // fall-through below.
      if (/\/versions(\?|$)/.test(url)) return json(versions.body ?? VERSIONS, versions.status ?? 200);
      if (url.includes("/profile")) return json(PROFILE);
      return json(VERSION);
    }),
  );
}

beforeEach(() => {
  routerReplace.mockClear();
  delete routeQuery.against;
  stub();
});
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

  it("shows no PSI band until a comparison is loaded", async () => {
    // The original defect: the dtype label borrowed `psiBand`'s colour when there was no
    // comparison at all, so the badge showed the colour of a band without the band. The
    // selector now exists, so the guard is that no band appears *before* one is chosen.
    const { container } = render(ProfileView, { props, ...mounted });
    await screen.findByText(/29,970 rows/);

    expect(container.innerHTML).not.toContain("text-amber-700");
    expect(container.innerHTML).not.toContain("text-red-700");
    // Carried over from the original guard: never true here, but still a real claim —
    // no rendered class is named after a PSI band before or after this change.
    expect(container.innerHTML).not.toContain("psi-");
    expect(screen.queryByText(/^PSI /)).not.toBeInTheDocument();
    // `ColumnDrift`'s `undefined` branch (nothing) is tested at the component level; this
    // pins the wiring that delivers `undefined` to it. `driftFor(column.name) ?? null`
    // would satisfy the component's own tests while making every card claim "new in this
    // version" before any reference is chosen — this is the assertion that catches that.
    expect(screen.queryByText(/new in this version/)).not.toBeInTheDocument();
  });

  it("bands each column once a reference is chosen", async () => {
    render(ProfileView, { props, ...mounted });
    const select = await screen.findByLabelText("Compare against");
    await userEvent.selectOptions(select, VERSIONS.items[1]?.id ?? "");

    // veh_brand moved 0.31 — above VR-DST-1's 0.25 fail threshold.
    expect(await screen.findByText(/PSI 0\.310/)).toHaveClass("text-red-700");
    // driv_age is continuous: no non-null top_levels, so no PSI and no band.
    expect(screen.getByText(/PSI not measured/)).toBeInTheDocument();
    // driv_age's mean_shift (1.35) is otherwise asserted nowhere: its unit, sign and
    // `.toFixed(3)` rendering could all change silently.
    expect(screen.getByText(/\+1\.350 mean/)).toBeInTheDocument();

    // Pin the comparison's direction. Every field above still renders for the swapped
    // call — an inverted comparison is a plausible-looking drift screen (every PSI, mean
    // shift and null-rate shift reads backwards, row_count_ratio is the reciprocal), not a
    // failure, so nothing else in this file would catch `compareProfiles(id, versionId)`.
    // `request()` calls `fetch` with a `URL`, not a string, so this reads pathname and
    // search rather than comparing against a literal — the origin is happy-dom's default.
    const fetchMock = fetch as unknown as { mock: { calls: unknown[][] } };
    const compareCall = fetchMock.mock.calls.find(([input]) =>
      String(input).includes("/compare"),
    );
    const compareUrl = new URL(String(compareCall?.[0]));
    expect(compareUrl.pathname).toBe(
      `/api/v1/dataset-versions/${PROFILE.dataset_version_id}/compare`,
    );
    expect(compareUrl.searchParams.get("against")).toBe(VERSIONS.items[1]?.id);
  });

  it("shows a top-level chip's level and count", async () => {
    // FR-DATA-49: top_levels is now a named object array, not an unnamed [level, count]
    // pair — the chip reads `.level`/`.count`, not tuple positions.
    render(ProfileView, { props, ...mounted });
    await screen.findByText(/29,970 rows/);
    expect(screen.getByText(/B12 · 8,000/)).toBeInTheDocument();
  });

  it("shows exposure on a chip when the level carries it, and omits it when not", async () => {
    render(ProfileView, { props, ...mounted });
    await screen.findByText(/29,970 rows/);
    // B12 carries exposure_years "4123.5" — rendered from the string, never parsed.
    expect(screen.getByText(/B12 · 8,000 · 4,123\.5/)).toBeInTheDocument();
    // B1 has no exposure_years at all — its chip has no exposure segment.
    const b1 = screen.getByText(/B1 · 5,000/);
    expect(b1.textContent).not.toMatch(/·.*·/);
  });

  it("renders a null level as missing, not as an empty or literal 'null' chip", async () => {
    const { container } = render(ProfileView, { props, ...mounted });
    await screen.findByText(/29,970 rows/);
    // A genuine null level (missing data) reads as the same "—" the rest of the view
    // uses for an absent value — never the empty string, never the word "null".
    const chips = container.querySelectorAll("article ul li");
    const chipTexts = Array.from(chips).map((chip) => chip.textContent);
    expect(chipTexts).toContain("— · 200 · 10.5");
    expect(chipTexts.some((text) => /null/i.test(text ?? ""))).toBe(false);
  });

  it("does not collide keys across chips sharing a null level", async () => {
    // Two rows could both carry `level: null`; keying on `level` alone would collide or
    // produce an `undefined` key. The list is a static, ordered slice, so all six chips
    // must still render distinctly.
    const { container } = render(ProfileView, { props, ...mounted });
    await screen.findByText(/29,970 rows/);
    const chips = container.querySelectorAll("article ul li");
    expect(chips).toHaveLength(3);
  });

  it("summarises what the profile covers", async () => {
    render(ProfileView, { props, ...mounted });
    expect(await screen.findByText(/29,970 rows/)).toBeInTheDocument();
    expect(screen.getByText(/2 candidate rating factors/)).toBeInTheDocument();
  });

  it("offers the other versions of the dataset, and never the one being viewed", async () => {
    render(ProfileView, { props, ...mounted });
    const select = await screen.findByLabelText("Compare against");
    const options = within(select).getAllByRole("option").map((o) => o.textContent?.trim());
    // v2 is the version on screen — comparing it with itself is PSI 0 everywhere.
    expect(options).not.toContain("v2");
    expect(options).toContain("v1");
  });

  it("disables a version that has no stored profile rather than offering a 404", async () => {
    // `compare` answers 404 NOT_FOUND for a reference with no profile. `profile_id` already
    // says so, so the refusal happens in the picker instead of after the request.
    render(ProfileView, { props, ...mounted });
    const select = await screen.findByLabelText("Compare against");
    const unprofiled = within(select).getByRole("option", { name: /v3 \(no profile\)/ });
    expect(unprofiled).toBeDisabled();
    // The opposite claim, proven separately: a profiled sibling stays selectable — only
    // the unprofiled one is refused.
    const profiled = within(select).getByRole("option", { name: "v1" });
    expect(profiled).not.toBeDisabled();
  });

  it("seeds the comparison from the URL and writes the choice back to it", async () => {
    routeQuery.against = "1";
    render(ProfileView, { props, ...mounted });
    const select = await screen.findByLabelText("Compare against");
    // Seeded from `?against=1` — the comparison is shareable as a link.
    await waitFor(() =>
      expect((select as HTMLSelectElement).value).toBe(VERSIONS.items[1]?.id),
    );

    await userEvent.selectOptions(select, "");
    expect(routerReplace).toHaveBeenCalledWith(
      expect.objectContaining({ query: expect.objectContaining({ against: undefined }) }),
    );

    // The other direction of the same watcher: choosing a version writes its *number*,
    // not its id, back into the query.
    await userEvent.selectOptions(select, VERSIONS.items[1]!.id);
    expect(routerReplace).toHaveBeenCalledWith(
      expect.objectContaining({ query: expect.objectContaining({ against: "1" }) }),
    );
  });

  it("ignores an ?against pointing at a version with no profile", async () => {
    // A stale or hand-edited link must not put the view into a state the endpoint refuses.
    routeQuery.against = "3";
    render(ProfileView, { props, ...mounted });
    const select = await screen.findByLabelText("Compare against");
    await waitFor(() => expect((select as HTMLSelectElement).value).toBe(""));
    // Rejecting the selection does not, on its own, change `referenceId` (it was already
    // `null`), so the write-back watcher never fires — the view must clear the query key
    // itself, or the address bar keeps advertising a comparison it just refused.
    expect(routerReplace).toHaveBeenCalledWith(
      expect.objectContaining({ query: expect.objectContaining({ against: undefined }) }),
    );
  });

  it("keeps the profile on screen when the versions list fails to load", async () => {
    // The picker is auxiliary (FR-DATA-27's refusal pattern, applied to the picker
    // itself): a 500 or 403 fetching the sibling versions must not blank an
    // already-loaded profile behind a full-page error.
    stub(200, ONE_WAY, {}, {
      status: 500,
      body: { title: "boom", status: 500, code: "INTERNAL", errors: [] },
    });
    render(ProfileView, { props, ...mounted });
    expect(await screen.findByText(/29,970 rows/)).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Compare against")).not.toBeInTheDocument();
  });

  it("states how the row count moved once a reference is chosen", async () => {
    render(ProfileView, { props, ...mounted });
    const select = await screen.findByLabelText("Compare against");
    await userEvent.selectOptions(select, VERSIONS.items[1]?.id ?? "");
    expect(await screen.findByText(/×1\.020 rows vs v1/)).toBeInTheDocument();
  });

  it("treats a reference version with no profile as an answer, not a failure", async () => {
    // The endpoint 404s when the *reference* has no stored profile. The picker disables
    // those, so this is the stale-link case: it must read as an explanation, not an alert.
    stub(200, ONE_WAY, {
      status: 404,
      body: {
        title: "This dataset version has no profile",
        status: 404,
        code: "NOT_FOUND",
        errors: [],
      },
    });
    render(ProfileView, { props, ...mounted });
    const select = await screen.findByLabelText("Compare against");
    await userEvent.selectOptions(select, VERSIONS.items[1]?.id ?? "");
    expect(await screen.findByText(/has no profile to compare against/)).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
});
