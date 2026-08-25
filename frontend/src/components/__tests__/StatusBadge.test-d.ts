import { describe, expectTypeOf, it } from "vitest";

import type { DatasetStatus } from "@/api/datasets";

/**
 * The property that makes `StatusBadge` worth being a component.
 *
 * Its tone map is `Record<DatasetStatus, string>`, so the **compiler** enumerates the
 * statuses. The inline map it replaced was `Record<string, string>` and had four of the
 * five members; the fifth, `failed`, fell through a `?? 'bg-slate-100'` fallback into
 * draft's own background and nothing anywhere complained.
 *
 * These assertions live in a `.test-d.ts` because `vitest.config.ts` sets
 * `typecheck.include: ["src/**\/*.test-d.ts"]` — a type error in a `.test.ts` file is
 * invisible to the runner and surfaces only under `vue-tsc`.
 */
describe("the status tone map's exhaustiveness", () => {
  it("knows all five statuses the contract declares", () => {
    // If `model-schema` adds a sixth, this fails here — before it fails as a badge with
    // no tone, which is the failure mode that has actually happened.
    expectTypeOf<DatasetStatus>().toEqualTypeOf<
      "draft" | "validating" | "validated" | "failed" | "archived"
    >();
  });

  it("refuses a tone map that omits a status", () => {
    // The positive proof: `@ts-expect-error` is itself an error when the line compiles
    // cleanly, so this fails if `Record<DatasetStatus, …>` ever stops being exhaustive.
    // @ts-expect-error - `archived` is missing, which is exactly what must not compile.
    const incomplete: Record<DatasetStatus, string> = {
      draft: "",
      validating: "",
      validated: "",
      failed: "",
    };
    expectTypeOf(incomplete).toEqualTypeOf<Record<DatasetStatus, string>>();
  });

  it("refuses a tone map with a status the contract does not declare", () => {
    // The other direction: a typo'd key is as silent as a missing one at runtime.
    const typo: Record<DatasetStatus, string> = {
      draft: "",
      validating: "",
      validated: "",
      failed: "",
      archived: "",
      // @ts-expect-error - not a DatasetStatus.
      validatedd: "",
    };
    expectTypeOf(typo).toEqualTypeOf<Record<DatasetStatus, string>>();
  });
});
