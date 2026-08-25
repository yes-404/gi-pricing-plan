import { describe, expect, it } from "vitest";

import factorsSource from "../../../../packages/pricing-core/src/pricing_core/modelling/factors.py?raw";

import {
  FACTOR_INTENT_LABELS,
  OFFERED_FACTOR_INTENTS,
  REFUSED_FACTOR_INTENTS,
} from "@/api/models";

/**
 * The refused intents against their executable authority.
 *
 * `FactorIntent` publishes four arms and the platform honours two. FR-MODEL-116 supersedes
 * `offset` and FR-MODEL-120 supersedes `diagnostic`, both **keeping the arm in the contract
 * deliberately** — so the union never narrows, and the permitted pair cannot be derived from
 * the type.
 *
 * What can be pinned is the **complement**. `REFUSED_FACTOR_INTENTS` in
 * `pricing-core/modelling/factors.py` is machine-readable and shared, so the frontend's copy
 * is checked against it rather than against prose. Pinning the *permitted* pair instead
 * would have no authority to check against, and a newly-live arm would silently vanish from
 * the picker with nothing failing.
 *
 * This runs on a `pricing-core` edit because `frontend.yml` already carries
 * `packages/pricing-core/src/pricing_core/modelling/**` on both triggers — the path
 * `builtinObjectives.test.ts` relies on. No CI change was needed.
 */
function refusedInPricingCore(): string[] {
  // Anchored on the assignment at line start. A bare-name scan would match the `__all__`
  // entry or a docstring mention and run on to the wrong mapping — the failure mode that
  // returned a plausible-but-wrong set when this guard's sibling was written.
  const table = /^REFUSED_FACTOR_INTENTS\s*:[^=]*=\s*MappingProxyType\(\s*\{([\s\S]*?)\n\s*\}\s*\)/m
    .exec(factorsSource);
  if (table?.[1] === undefined) {
    throw new Error(
      "Could not find REFUSED_FACTOR_INTENTS in pricing_core/modelling/factors.py. If it " +
        "was restructured, update this guard — do not delete it: the frontend's copy is " +
        "then unchecked, and a superseded intent reaches a fit.",
    );
  }
  return Array.from(
    table[1].matchAll(/FactorIntent\.([A-Z_]+)\s*:/g),
    (match) => (match[1] as string).toLowerCase(),
  );
}

describe("the factor intents the platform refuses", () => {
  it("finds the mapping it is scraping", () => {
    // The control. Every assertion below is vacuous if the pattern matched nothing, and a
    // guard green because it read an empty set is worse than no guard.
    expect(refusedInPricingCore().length).toBeGreaterThan(0);
  });

  it("refuses exactly what pricing-core refuses", () => {
    // Set equality both ways. A frontend list that is a *subset* offers an intent the fit
    // will reject — accepted, stored, audited, then detonating at fit, because `POST
    // /factors` has no such refusal. A *superset* hides one the platform still honours.
    expect([...REFUSED_FACTOR_INTENTS].sort()).toEqual(refusedInPricingCore().sort());
  });

  it("offers every published arm that is not refused", () => {
    expect([...OFFERED_FACTOR_INTENTS].sort()).toEqual(["control", "risk"]);
  });

  it("labels every arm the contract publishes, including the refused ones", () => {
    // The `Record` covers the whole union so the compiler enumerates it; a fifth arm is a
    // build error rather than a missing option. That means the refused arms carry labels
    // too, which is correct — an existing Factor may still carry one and want naming.
    expect(Object.keys(FACTOR_INTENT_LABELS).sort()).toEqual(
      ["control", "diagnostic", "offset", "risk"],
    );
  });
});
