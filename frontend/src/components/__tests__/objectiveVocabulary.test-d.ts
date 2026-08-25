import { describe, expectTypeOf, it } from "vitest";

import {
  FAMILIES,
  LINKS,
  RESPONSES,
  type GlmSpec,
  type ModelSpec,
} from "@/api/modelSpecs";

/**
 * The option lists against the unions they are copies of, **both directions**.
 *
 * `satisfies readonly GlmSpec["family"][]` on the arrays catches only one direction: a
 * member the contract *removed*, which the array would then still offer. A member the
 * contract *added* passes, because a subset satisfies the constraint — and the picker
 * silently stops offering something the platform accepts.
 *
 * `toEqualTypeOf` closes that. It is the `SpecProblemList.test-d.ts` precedent: the union
 * and the list must be the same set, so a member added anywhere fails here and tells
 * whoever added it where the option list lives. `.test-d.ts` because `vitest.config.ts`
 * restricts `typecheck.include` to that pattern.
 */
describe("the builder's option vocabularies", () => {
  it("offers exactly the GLM families the contract declares", () => {
    expectTypeOf<GlmSpec["family"]>().toEqualTypeOf<(typeof FAMILIES)[number]>();
  });

  it("offers exactly the GLM links the contract declares", () => {
    // FR-MODEL-18 names five; `power(k)` "remains declared and unbuilt — `GlmSpec` has no
    // spelling for it and no slice has needed one", staged under FR-MODEL-87 rather than
    // dropped (`02`:129-139). The picker binds to the four the contract has, and a fifth
    // arriving in the contract announces itself here.
    expectTypeOf<GlmSpec["link"]>().toEqualTypeOf<(typeof LINKS)[number]>();
  });

  it("offers exactly the response kinds the contract declares", () => {
    expectTypeOf<NonNullable<ModelSpec["response"]>>().toEqualTypeOf<
      (typeof RESPONSES)[number]
    >();
  });
});
