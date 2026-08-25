import { assertType, describe, expectTypeOf, it } from "vitest";

import type { Uncertainty, UncertaintyBasis, UnavailableReason } from "@/api/predictions";
import { intervalClaim } from "@/api/predictions";

describe("the uncertainty contract", () => {
  it("publishes exactly five unavailable reasons", () => {
    // FR-MODEL-77's three, FR-MODEL-93's fourth, FR-MODEL-124's fifth. A sixth arriving in
    // the generated types breaks `unavailableCopy`'s exhaustive switch at compile time; this
    // assertion says the same thing where a reader will see it.
    expectTypeOf<UnavailableReason>().toEqualTypeOf<
      | "no_interval_models_fitted"
      | "interval_models_not_approved"
      | "interval_models_stale"
      | "covariance_not_stored"
      | "model_type_has_no_interval"
    >();
  });

  it("publishes exactly two bases (FR-MODEL-99)", () => {
    expectTypeOf<UncertaintyBasis>().toEqualTypeOf<
      "information_matrix" | "unpenalised_information_matrix"
    >();
  });

  it("does not encode FR-MODEL-101's exclusions in the type", () => {
    // FR-MODEL-101 forbids `basis` on a quantile pair and requires `interval_models` on it.
    // The generated `Uncertainty` is a flat object with every field nullable, so neither
    // rule is expressible here and a runtime check cannot be replaced by a type. This
    // assertion records that deliberately: it is why `PredictionUncertainty.vue` branches on
    // `kind` rather than on field presence.
    assertType<Uncertainty>({
      kind: "quantile_pair_interval",
      basis: "information_matrix",
      level: 0.95,
      reason: null,
      interval_models: null,
    });
  });

  it("refuses `unavailable` where an interval claim is required", () => {
    // @ts-expect-error `unavailable` carries no interval, so it makes no claim.
    intervalClaim("unavailable");
  });
});
