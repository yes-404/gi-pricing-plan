import { render, screen } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import type { PredictedRow, Uncertainty, UnavailableReason } from "@/api/predictions";
import PredictionUncertainty from "@/components/PredictionUncertainty.vue";

const ROW: PredictedRow = { expected: 0.1342, lower: 0.1201, upper: 0.1489 };

function mount(uncertainty: Uncertainty, row: PredictedRow = ROW) {
  return render(PredictionUncertainty, { props: { uncertainty, row } });
}

describe("a GLM confidence interval", () => {
  const GLM: Uncertainty = {
    kind: "confidence_interval_mean",
    basis: "information_matrix",
    level: 0.95,
    reason: null,
    interval_models: null,
  };

  it("states the level and both bounds", () => {
    mount(GLM);
    expect(screen.getByText(/95%/)).toBeTruthy();
    expect(screen.getByText(/0\.1201/)).toBeTruthy();
    expect(screen.getByText(/0\.1489/)).toBeTruthy();
  });

  it("says the interval is about the average, not an individual (FR-196)", () => {
    mount(GLM);
    expect(screen.getByText(/average outcome/)).toBeTruthy();
  });

  it("states the basis (FR-197)", () => {
    mount(GLM);
    expect(screen.getByTestId("uncertainty-basis").textContent).toContain("information matrix");
  });

  it("warns that an unpenalised basis makes the interval too wide (FR-197)", () => {
    mount({ ...GLM, basis: "unpenalised_information_matrix" });
    const basis = screen.getByTestId("uncertainty-basis").textContent ?? "";
    expect(basis).toContain("wider");
  });
});

describe("a paired-quantile interval", () => {
  // `level` is 0.9, not 0.95, and that is not a typo. `Uncertainty`'s validator pins it to the
  // alpha spread: "a 0.05/0.95 pair covers 0.90, and a response claiming 0.95 from it
  // overstates its own coverage by exactly the amount a reader cannot see." A fixture with
  // level 0.95 here could not be produced by the backend.
  const PAIR: Uncertainty = {
    kind: "quantile_pair_interval",
    basis: null,
    level: 0.9,
    reason: null,
    interval_models: {
      lower_model_id: "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
      upper_model_id: "dddddddd-dddd-4ddd-8ddd-dddddddddddd",
      lower_alpha: 0.05,
      upper_alpha: 0.95,
    },
  };

  it("says the interval is about an individual outcome (FR-201)", () => {
    mount(PAIR);
    expect(screen.getByText(/individual outcome/)).toBeTruthy();
  });

  it("renders no basis, because FR-201 forbids one on this kind", () => {
    mount(PAIR);
    expect(screen.queryByTestId("uncertainty-basis")).toBeNull();
  });

  it("ignores a basis the server should not have sent, rather than displaying it", () => {
    // Defence in depth, and deliberately so. `Uncertainty`'s model validator already refuses
    // this server-side, citing FR-201 by name — "a pair of quantile fits has no
    // covariance matrix; stating one would claim inference this interval did not do". But the
    // generated TypeScript type is a flat object with every field nullable and cannot express
    // that, so the component branches on `kind` rather than on field presence. A stray basis
    // rendered here would attach a GLM's claim to a GBM's bound.
    mount({ ...PAIR, basis: "information_matrix" });
    expect(screen.queryByTestId("uncertainty-basis")).toBeNull();
  });

  it("names both bound models and their alphas (FR-199)", () => {
    mount(PAIR);
    const bounds = screen.getByTestId("interval-models").textContent ?? "";
    expect(bounds).toContain("0.05");
    expect(bounds).toContain("0.95");
  });
});

describe("an unavailable interval", () => {
  // `UnavailableReason | null`, not `Uncertainty["reason"]`: the latter also admits
  // `undefined` (the field is optional as well as nullable), and under
  // `exactOptionalPropertyTypes` writing `reason: undefined` into the literal below is a type
  // error rather than an omitted key. The absent-key case is the contract's, not this
  // helper's, and the component normalises both.
  function unavailable(reason: UnavailableReason | null): Uncertainty {
    return { kind: "unavailable", basis: null, level: null, reason, interval_models: null };
  }

  it("still shows the expectation (FR-195)", () => {
    mount(unavailable("covariance_not_stored"), { expected: 0.1342, lower: null, upper: null });
    expect(screen.getByText(/0\.1342/)).toBeTruthy();
  });

  it("gives FR-200(ii)'s reading of `not_approved`", () => {
    mount(unavailable("interval_models_not_approved"));
    expect(screen.getByText(/less advanced/)).toBeTruthy();
  });

  it("gives FR-200(iii)'s reading of `stale`", () => {
    // `getAllByText`: both the headline and the detail say "superseded", and `getByText`
    // throws on a second match. The requirement is that the copy states supersession, not
    // that it states it exactly once.
    mount(unavailable("interval_models_stale"));
    expect(screen.getAllByText(/superseded/).length).toBeGreaterThan(0);
  });

  it("names the EBM refusal rather than a reason false of an EBM (FR-180)", () => {
    mount(unavailable("model_type_has_no_interval"));
    expect(screen.getByText(/offers no interval/)).toBeTruthy();
  });

  it("renders a null reason as a stated gap, never as silence", () => {
    // `reason` is nullable in the contract while FR-194 requires "an explicit
    // `uncertainty: unavailable` with the reason". A null is therefore a server-side
    // requirement breach, and the page says so rather than showing an empty panel.
    mount(unavailable(null));
    expect(screen.getByText(/no reason/i)).toBeTruthy();
  });
});
