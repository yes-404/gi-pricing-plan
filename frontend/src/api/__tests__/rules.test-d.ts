import { describe, expectTypeOf, it } from "vitest";

import { createRule, type RuleCreate } from "@/api/rules";

/**
 * `RuleCreate` is generated from the OpenAPI document, so this is not a restatement of the
 * backend's shape — it is the assertion that the frontend reads the generated one at all.
 * The hand-written body it replaces omitted `catalogue_id`, which is how `W6b-13b`'s
 * backend change never reached the browser (`FR-DATA-53`).
 */
describe("createRule's request body", () => {
  it("is the generated RuleCreate, so catalogue_id survives", () => {
    expectTypeOf(createRule).parameter(0).toEqualTypeOf<RuleCreate>();
    expectTypeOf<RuleCreate>().toHaveProperty("catalogue_id");
    expectTypeOf<RuleCreate>().toHaveProperty("message");
  });
});
