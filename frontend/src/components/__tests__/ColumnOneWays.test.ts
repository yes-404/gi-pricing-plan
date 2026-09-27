import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import type { OneWaySummary } from "@/api/profiles";
import { cellUnder } from "@/test-tables";

import ColumnOneWays from "../ColumnOneWays.vue";

function summary(over: Partial<OneWaySummary> = {}): OneWaySummary {
  return {
    column: "vehicle_age",
    rows: [
      {
        level: "0-3",
        exposure_years: "1234.560000",
        claim_count: 90,
        claim_amount_minor: 26758000,
        frequency: 0.0729,
        frequency_ci: [0.0586, 0.0895],
        mean_severity: 5000,
        severity_ci: [4100, 6050],
        mean_burning_cost: 365,
      },
      {
        level: "4+",
        exposure_years: "800.000000",
        claim_count: 1,
        claim_amount_minor: 12000,
        frequency: 0.00125,
        frequency_ci: [0.0, 0.007],
        mean_severity: null,
        severity_ci: null,
        mean_burning_cost: null,
      },
    ],
    ...over,
  } as OneWaySummary;
}

function table(oneWays: OneWaySummary[] = [summary()]): HTMLElement {
  render(ColumnOneWays, { props: { oneWays } });
  return screen.getByRole("table", { name: /one-way summary for vehicle_age/i });
}

describe("the candidate column list", () => {
  it("names each column and how many levels its one-way has", () => {
    render(ColumnOneWays, { props: { oneWays: [summary()] } });

    expect(screen.getByText("vehicle_age")).toBeInTheDocument();
    expect(screen.getByText(/2 levels/)).toBeInTheDocument();
  });

  it("shows the stored numbers exactly as the profile carries them", () => {
    // FR-61: computed once, in the profiling pass. `exposure_years` is an exact
    // decimal string and is formatted without being parsed — a float64 round-trip is what
    // FR-10 exists to prevent.
    const t = table();

    expect(cellUnder(t, /0-3/, "Exposure")).toHaveTextContent("1,234.56");
    expect(cellUnder(t, /0-3/, "Claims")).toHaveTextContent("90");
    expect(cellUnder(t, /0-3/, "Frequency")).toHaveTextContent("0.0729");
  });

  it("carries the interval beside the frequency it belongs to", () => {
    // FR-61 puts an exact Poisson interval on the frequency, and a frequency without
    // one invites a decision the claim count cannot support.
    expect(cellUnder(table(), /0-3/, "Frequency CI")).toHaveTextContent("0.0586–0.0895");
  });

  it("scales the minor-unit statistics without dressing them as currency", () => {
    // `mean_severity` and `mean_burning_cost` are statistics in minor units, not amounts
    // (FR-64). No symbol, because none is knowable here — and none is owed.
    const t = table();

    expect(cellUnder(t, /0-3/, "Severity")).toHaveTextContent("50.00");
    expect(cellUnder(t, /0-3/, "Burning cost")).toHaveTextContent("3.65");
    expect(t.textContent).not.toMatch(/[£$€]/);
  });

  it("renders an absent statistic as absent rather than as zero", () => {
    // The second level has one claim, below `gamma_severity_interval`'s two-claim floor.
    const t = table();

    expect(cellUnder(t, /4\+/, "Severity")).toHaveTextContent("—");
    expect(cellUnder(t, /4\+/, "Frequency CI")).toHaveTextContent("0.0000–0.0070");
  });

  it("does not show the incurred amount, which needs a currency this view cannot reach", () => {
    // Not a styling choice. `claim_amount_minor` is minor units of the workspace currency;
    // the workbench holds a dataset *version* id, `DatasetVersion` carries no currency, and
    // `/datasets/{dataset_id}` is PATCH-only. Rendering it bare would show minor units as
    // if they were units; guessing GBP is what OQ-551 exists to stop. The fixture's
    // 26758000 would appear as some rendering of itself if the column were ever added back
    // without a currency, so this asserts the digits are absent entirely.
    const t = table();

    expect(t.textContent).not.toContain("26758000");
    expect(t.textContent).not.toContain("267,580");
    expect(within(t).queryAllByRole("columnheader").map((h) => h.textContent?.trim()))
      .not.toContain("Incurred");
  });

  it("says so when a version's profile records no one-ways", () => {
    render(ColumnOneWays, { props: { oneWays: [] } });

    expect(screen.getByText(/records no one-ways/)).toBeInTheDocument();
  });
});
