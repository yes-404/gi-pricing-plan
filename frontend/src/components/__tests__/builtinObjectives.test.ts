import { describe, expect, it } from "vitest";

// Vite's own `?raw`, not `node:fs`. `tsconfig.app.json` declares `types: ["vite/client"]`
// and no node types, deliberately — the app has no business seeing node globals — and
// `?raw` is the toolchain's supported way to read a file as text, declared by
// `vite/client` itself. It also resolves at build time, so a path that stops existing is
// a build failure rather than a runtime throw inside one test.
import gbmSource from "../../../../packages/pricing-core/src/pricing_core/modelling/gbm.py?raw";
import objectivesSource from "../../../../packages/model-schema/src/model_schema/objectives.py?raw";

import { BUILTIN_GBM_OBJECTIVES } from "@/api/modelSpecs";
import { FITTABLE_OBJECTIVE_STATUSES } from "@/api/objectives";

/**
 * The divergence guard for OQ-MODEL-37, and the only part of it this slice can build.
 *
 * `SUPPORTED_GBM_OBJECTIVES` in `pricing_core/modelling/gbm.py` is FR-MODEL-26's set —
 * the authoritative answer to "which builtin objectives does the platform support?" — and
 * it reaches no contract: `model-schema` depends on pydantic alone and cannot import it,
 * `generated.json` has zero occurrences of `count:poisson`, and the hand-authored schema
 * lists the four inside a description string ending in an ellipsis, "Not an enum".
 * `GbmFunctionRef.name` is open on purpose, because the same type carries `eval_metrics`,
 * whose vocabulary is the backend's own.
 *
 * So the frontend authors the list, which is the second hand-written copy the Python
 * file's own comment warns against:
 *
 *   "Two hand-written lists would eventually disagree about which objectives the platform
 *    supports, and the disagreement would show up as a spec that validated and then
 *    failed."
 *
 * This test cannot remove the second list — that is OQ-MODEL-37(a), a `model-schema`
 * change with no owner. It converts the divergence that comment predicts from silent into
 * a red test: the difference between shipping a spec that validates and then fails, and
 * finding out at `pnpm test`.
 *
 * **The guard only runs because `frontend.yml` gained
 * `packages/pricing-core/src/pricing_core/modelling/**`.** `python.yml` carries no
 * `frontend/**`, so on the Python side nothing would run when someone edited the
 * TypeScript half — and a check that cannot run is not enforcement, which `python.yml`'s
 * own `tests/**` comment says after being bitten three times.
 */

/** The keys of `_OBJECTIVES`, which `SUPPORTED_GBM_OBJECTIVES` is a frozenset over. */
function objectivesDeclaredInPricingCore(): string[] {
  // The annotation is `Final[dict[str, tuple[str, str, Literal["exp", "logistic"]]]]`, so
  // the type is matched lazily to the first `] = {` rather than with `[^\]]*` — nested
  // brackets stop a negated class at the wrong one. The control test below caught that.
  const table = /_OBJECTIVES:\s*Final\[[\s\S]*?\]\s*=\s*\{([\s\S]*?)\n\}/.exec(gbmSource);
  if (table?.[1] === undefined) {
    throw new Error(
      "Could not find the _OBJECTIVES table in pricing_core/modelling/gbm.py. If it was " +
        "restructured, update this guard — do not delete it, because the divergence it " +
        "catches is otherwise silent (OQ-MODEL-37).",
    );
  }
  return Array.from(table[1].matchAll(/^\s*"([^"]+)":/gm), (match) => match[1] as string);
}

/**
 * OQ-MODEL-37's **second surface**, added by W6b-4b.
 *
 * `FITTABLE_OBJECTIVE_STATUSES` is `{certified, review, approved}` — the statuses a fit
 * accepts, and deliberately *not* R4's `approved`-alone rule for a model reaching
 * approval. `ObjectiveStatus` is a generated schema so the **type** reaches every client,
 * but the **subset** reaches none: `ObjectivePicker` must hand-write it.
 *
 * Option (a) — narrowing a field's type — cannot express this one, because a subset of an
 * enum's members is not a field type. So the divergence test is the whole of the interim
 * here, not a stopgap alongside a better fix.
 */
function fittableStatusesDeclaredInModelSchema(): string[] {
  // Anchored on the **assignment**, at line start. The bare name matches its `__all__`
  // entry ninety lines earlier, and a lazy scan from there reaches the *transitions*
  // table's first `frozenset` instead — which returned `{certified, deprecated}`, a
  // plausible-looking set that is not this one. Caught by the equality assertion below and
  // not by the "found something" control, which is the limit of that kind of control.
  const table =
    /^FITTABLE_OBJECTIVE_STATUSES\s*:[^=]*=\s*frozenset\(\s*\{([\s\S]*?)\}\s*\)/m.exec(
      objectivesSource,
    );
  if (table?.[1] === undefined) {
    throw new Error(
      "Could not find FITTABLE_OBJECTIVE_STATUSES in model_schema/objectives.py. If it " +
        "was restructured, update this guard — do not delete it (OQ-MODEL-37).",
    );
  }
  return Array.from(
    table[1].matchAll(/ObjectiveStatus\.([A-Z_]+)/g),
    (match) => (match[1] as string).toLowerCase(),
  );
}

describe("the fittable objective statuses against model-schema", () => {
  it("finds the set it is scraping", () => {
    expect(fittableStatusesDeclaredInModelSchema().length).toBeGreaterThan(0);
  });

  it("offers exactly the statuses a fit accepts", () => {
    // A subset would make the picker stricter than the fit — an actuary unable to select
    // an objective the platform accepts, which is the mistake this slice's own plan made
    // before arbitration. A superset would offer one the fit refuses.
    expect([...FITTABLE_OBJECTIVE_STATUSES].sort()).toEqual(
      fittableStatusesDeclaredInModelSchema().sort(),
    );
  });
});

describe("the builtin GBM objective list against pricing-core", () => {
  it("finds the table it is scraping", () => {
    // The control. Every assertion below is vacuous if the pattern silently matched
    // nothing, and a guard that passes because it found nothing is worse than no guard.
    expect(objectivesDeclaredInPricingCore().length).toBeGreaterThan(0);
  });

  it("offers exactly the objectives pricing-core supports", () => {
    // Set equality both ways. A frontend list that is a *subset* hides an objective the
    // platform supports; a *superset* offers one the fit will refuse — which is the "spec
    // that validated and then failed" the Python comment predicts.
    expect([...BUILTIN_GBM_OBJECTIVES].sort()).toEqual(
      objectivesDeclaredInPricingCore().sort(),
    );
  });
});
