import { request } from "./client";
import type { components } from "./generated/schema";

/**
 * The union `02` §4.4 defines, and the reason this slice builds three objective controls
 * rather than one: `GlmSpec` carries `family` × `link`, `GbmSpec` an objective
 * `GbmFunctionRef`, `EbmSpec` the literal `"rmse" | "mae"`. Three shapes `model-schema`
 * keeps apart, so nothing here normalises them into a fourth (`CLAUDE.md` §2).
 */
export type ModelSpec = components["schemas"]["ModelSpecValidate"]["spec"];
export type GlmSpec = components["schemas"]["GlmSpec"];
export type GbmSpec = components["schemas"]["GbmSpec"];
export type EbmSpec = components["schemas"]["EbmSpec"];
export type GbmFunctionRef = components["schemas"]["GbmFunctionRef"];
export type SpecValidation = components["schemas"]["SpecValidation"];
export type SpecProblem = components["schemas"]["SpecProblem"];
export type SpecProblemKind = components["schemas"]["SpecProblemKind"];

/**
 * "May this be fitted?", without fitting it (`02` §5.1, FR-MODEL-44, FR-MODEL-81).
 *
 * **A 200 carrying `ok: false` is a result, not a failure.** `02` §5.1's row is explicit:
 * "a spec that merely cannot be fitted is not a bad *request*, so it is not a 4xx". This
 * function therefore resolves for a refused spec and the caller renders its problems — it
 * is only `request`'s own error path, and so a `ProblemError`, when the request itself was
 * bad. The one case that *is* an error here is a spec naming a version that does not
 * exist, which the same row makes a **404**: a different code path with a different
 * meaning, and a caller that funnels both through one handler loses the distinction the
 * row was written to draw.
 *
 * The response carries every problem rather than the first — see `SpecValidation`'s own
 * docstring in the contract, which explains that a builder surfacing one error at a time
 * "would make a ten-factor spec a ten-round conversation".
 */
export function validateSpec(spec: ModelSpec): Promise<SpecValidation> {
  // The body wraps the spec — `ModelSpecValidate` is `{ spec }`, not the spec itself.
  return request<SpecValidation>("/model-specs/validate", {
    method: "POST",
    body: { spec },
  });
}
