import { describe, expectTypeOf, it } from "vitest";

import { psiBand } from "@/api/profiles";

/**
 * `psiBand`'s parameter, asserted at the type level.
 *
 * `compare_profiles` returns `psi: null` for any column with no non-null `top_levels` —
 * every continuous column, in practice. The old signature accepted `psi: number | null |
 * undefined` and answered `"stable"` for the null case, so an unmeasured column rendered
 * as a calm band the moment this slice gave the function its first caller. Narrowing the
 * parameter to a plain `number` makes that a compile error instead: a caller must guard
 * `psi != null` before calling, rather than getting a silent default.
 */
describe("psiBand's argument", () => {
  it("takes a number, not a nullable one", () => {
    expectTypeOf(psiBand).parameter(0).toEqualTypeOf<number>();
  });

  it("takes the rule's warn_above, not a literal baked into the caller", () => {
    // `W6b-13`: the second argument is required. A caller that omits it — or passes
    // something nullable — must fail `type-check`, not silently band against nothing.
    expectTypeOf(psiBand).parameter(1).toEqualTypeOf<number>();
  });
});
