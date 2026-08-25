import { describe, expectTypeOf, it } from "vitest";

import type { SpecProblemKind } from "@/api/modelSpecs";

/**
 * The property that makes `SpecProblemList`'s label map worth typing on the union.
 *
 * `SpecProblemKind` is documented in the contract as "a closed set, **because the frontend
 * renders each differently** and an open string would make that a guess about wording" —
 * so the requirement that the frontend cover every member is stated by the contract, not
 * invented here. `Record<SpecProblemKind, string>` makes the compiler enforce it.
 *
 * These assertions live in a `.test-d.ts` because `vitest.config.ts` restricts
 * `typecheck.include` to that pattern; a type error in a `.test.ts` is invisible to the
 * runner and surfaces only under `vue-tsc`.
 */
describe("the spec problem kind union", () => {
  it("has exactly the eleven members the component maps", () => {
    // A twelfth added to the contract fails here first — before it fails as a problem
    // rendering with a blank heading, which is what a `Record<string, string>` would do.
    expectTypeOf<SpecProblemKind>().toEqualTypeOf<
      | "dataset_not_validated"
      | "factor_missing"
      | "factor_prohibited"
      | "factor_unresolvable"
      | "split_missing"
      | "split_invalid"
      | "response_missing"
      | "offset_missing"
      | "model_offset_unresolvable"
      | "complexity_limit"
      | "objective_unsupported"
    >();
  });

  it("refuses a label map that omits a kind", () => {
    // `@ts-expect-error` is itself an error when the line compiles cleanly, so this fails
    // if `Record<SpecProblemKind, …>` ever stops being exhaustive.
    // @ts-expect-error - `objective_unsupported` is missing, which must not compile.
    const incomplete: Record<SpecProblemKind, string> = {
      dataset_not_validated: "",
      factor_missing: "",
      factor_prohibited: "",
      factor_unresolvable: "",
      split_missing: "",
      split_invalid: "",
      response_missing: "",
      offset_missing: "",
      model_offset_unresolvable: "",
      complexity_limit: "",
    };
    expectTypeOf(incomplete).toEqualTypeOf<Record<SpecProblemKind, string>>();
  });
});
