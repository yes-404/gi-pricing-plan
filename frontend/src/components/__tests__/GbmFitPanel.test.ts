import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import type { GbmFitResult, GbmSpec } from "@/api/models";

import GbmFitPanel from "../GbmFitPanel.vue";

const SPEC: GbmSpec = {
  model_type: "lightgbm",
  model_family_slug: "motor-ad-frequency",
  dataset_version_id: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
  response_column: "ad_claim_count",
  objective: { kind: "builtin", name: "count:poisson" },
  categorical_handling: "native",
  eval_metrics: [{ kind: "builtin", name: "poisson-nloglik" }],
  factors: ["driver_age_banded", "vehicle_group_rated", "region_grouped"],
  interaction_constraints: [],
  loss_treatment: { kind: "none" },
  monotone_constraints: "derived_from_factors",
  offset: { kind: "log_column", column: "exposure_years" },
  weight: { kind: "none" },
  seed: 0,
  early_stopping: { metric: "poisson-nloglik", on: "holdout", rounds: 50 },
  interval_for: null,
};

const FIT: GbmFitResult = {
  model_type: "lightgbm",
  booster_blob: { sha256: "b".repeat(64), bytes: 184320, media_type: "text/plain" },
  booster_format: "lightgbm_text",
  feature_order: ["driver_age_banded", "vehicle_group_rated", "region_grouped"],
  feature_dtypes: {
    driver_age_banded: "ord",
    vehicle_group_rated: "cat",
    region_grouped: "cat",
  },
  categorical_maps: { region_grouped: { north: 0, midlands: 1, south: 2 } },
  monotone_constraints: [-1, 1, 0],
  base_margin: { kind: "log_column", column: "exposure_years" },
  best_iteration: 184,
  inverse_link: null,
  rows: 542410,
  fit_seconds: 41.7,
  library_versions: { lightgbm: "4.7.0" },
  dropped_eval_metrics: [
    { name: "rmse", reason: "builtin_evaluated_before_custom_stopping_metric" },
  ],
};

describe("the GBM arm panel", () => {
  it("names each monotone constraint against the feature it constrains", () => {
    // The constraint vector is positional against `feature_order`. Rendered on its own it is
    // three integers; against the order it is the judgement the fit encodes.
    render(GbmFitPanel, { props: { spec: SPEC, fit: FIT } });
    const table = screen.getByRole("table", { name: "Features and constraints" });
    const row = within(table).getByText("driver_age_banded").closest("tr")!;
    expect(row).toHaveTextContent("decreasing");
    expect(within(table).getByText("region_grouped").closest("tr")!).toHaveTextContent("none");
  });

  it("says a constraint direction in words, never in colour alone", () => {
    // NFR-OVR-10. A red or green arrow is not a channel a screen reader has.
    render(GbmFitPanel, { props: { spec: SPEC, fit: FIT } });
    expect(screen.getByText("increasing")).toBeInTheDocument();
  });

  it("says who applies the inverse link, for both readings of the field", () => {
    // FR-MODEL-94: null means the library already transformed; a value means the platform
    // must. The value alone cannot distinguish them, so the page says which.
    render(GbmFitPanel, { props: { spec: SPEC, fit: FIT } });
    expect(screen.getByText(/library has already applied/i)).toBeInTheDocument();

    render(GbmFitPanel, { props: { spec: SPEC, fit: { ...FIT, inverse_link: "exp" } } });
    expect(screen.getByText(/platform applies exp/i)).toBeInTheDocument();
  });

  it("reports a declared eval metric the backend did not evaluate", () => {
    // FR-MODEL-111. Silent absence is exactly the defect the field was added to remove.
    render(GbmFitPanel, { props: { spec: SPEC, fit: FIT } });
    expect(screen.getByText(/rmse/)).toBeInTheDocument();
    expect(screen.getByText(/not evaluated/i)).toBeInTheDocument();
  });

  it("says nothing about dropped metrics when none were dropped", () => {
    render(GbmFitPanel, { props: { spec: SPEC, fit: { ...FIT, dropped_eval_metrics: [] } } });
    expect(screen.queryByText(/not evaluated/i)).toBeNull();
  });

  it("says the offset entered as a base margin, not as a feature", () => {
    // FR-MODEL-27. Exposure entering as a feature or a weight is the difference between a
    // frequency model and a nonsense one, and the fit result is where what was actually
    // constructed is recorded.
    render(GbmFitPanel, { props: { spec: SPEC, fit: FIT } });
    expect(screen.getByText(/base margin/i)).toBeInTheDocument();
    expect(screen.getByText(/log\(exposure_years\)/)).toBeInTheDocument();
  });

  it("names the early-stopping metric and what it stopped on", () => {
    // FR-MODEL-30 refuses training-set stopping. The metric and the partition are what say
    // the stop was honest; "early stopping: on" says nothing a reader can check.
    render(GbmFitPanel, { props: { spec: SPEC, fit: FIT } });
    expect(screen.getByText(/poisson-nloglik/)).toBeInTheDocument();
    expect(screen.getByText(/holdout/)).toBeInTheDocument();
  });
});
