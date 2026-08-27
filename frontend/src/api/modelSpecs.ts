import { request } from "./client";
import type { components } from "./generated/schema";
import type { components as requestComponents } from "./generated/schema.requests";

/**
 * The union `02` §4.4 defines, and the reason this slice builds three objective controls
 * rather than one: `GlmSpec` carries `family` × `link`, `GbmSpec` an objective
 * `GbmFunctionRef`, `EbmSpec` the literal `"rmse" | "mae"`. Three shapes `model-schema`
 * keeps apart, so nothing here normalises them into a fourth (`CLAUDE.md` §2).
 *
 * Alias from the **permissive** generated set (OQ-PLAT-16 (c)): this type shapes a request
 * body, where a server-defaulted property may be omitted. The strict set (the default
 * `--default-non-nullable`) shapes responses, whose defaults are always present.
 */
export type ModelSpec = requestComponents["schemas"]["ModelSpecValidate"]["spec"];
export type GlmSpec = components["schemas"]["GlmSpec"];
export type GbmSpec = components["schemas"]["GbmSpec"];
export type EbmSpec = components["schemas"]["EbmSpec"];
export type GbmFunctionRef = components["schemas"]["GbmFunctionRef"];
export type SpecValidation = components["schemas"]["SpecValidation"];
export type SpecProblem = components["schemas"]["SpecProblem"];
export type SpecProblemKind = components["schemas"]["SpecProblemKind"];

export type GlmFamily = GlmSpec["family"];
export type GlmLink = GlmSpec["link"];
export type ResponseKind = NonNullable<ModelSpec["response"]>;

/**
 * The builder's option lists, **derived from the generated unions and pinned to them**.
 *
 * `satisfies` catches a member the contract removed; `objectiveVocabulary.test-d.ts`'s
 * `toEqualTypeOf` catches one it added, which `satisfies` cannot — a subset satisfies the
 * constraint and the picker just stops offering something the platform accepts. The two
 * together are what a generated enum would give for free.
 *
 * They live here rather than in the view so the type test can import them: a list the test
 * cannot see is a list the pin does not cover.
 */
export const FAMILIES = ["poisson", "negative_binomial", "gamma", "inverse_gaussian",
  "tweedie", "binomial", "gaussian"] as const satisfies readonly GlmFamily[];
export const LINKS = ["log", "logit", "identity", "inverse"] as const satisfies readonly GlmLink[];
export const RESPONSES = ["claim_count", "claim_severity", "burning_cost",
  "conversion", "retention"] as const satisfies readonly ResponseKind[];

/**
 * FR-MODEL-26's builtin GBM objectives, in XGBoost's vocabulary.
 *
 * **This is a second hand-written copy of a set the platform owns elsewhere**, and the
 * file that owns it says so: `SUPPORTED_GBM_OBJECTIVES` in
 * `pricing_core/modelling/gbm.py` is the authority, and its comment warns that "two
 * hand-written lists would eventually disagree about which objectives the platform
 * supports, and the disagreement would show up as a spec that validated and then failed".
 *
 * It exists here because the set reaches no contract — `GbmFunctionRef.name` is
 * deliberately open, since the same type carries `eval_metrics` whose vocabulary is the
 * backend's own, and `model-schema` depends on pydantic alone so it cannot import the set.
 * That is **OQ-MODEL-37**, whose option (a) removes this constant rather than policing it,
 * and which has no owner because `W32` is closed.
 *
 * Until then `builtinObjectives.test.ts` reads `gbm.py` as text and fails when the two
 * disagree, so the divergence the Python comment predicts is loud rather than silent.
 * **Do not edit this list without editing that file, and do not delete the test.**
 */
export const BUILTIN_GBM_OBJECTIVES = [
  "count:poisson",
  "reg:gamma",
  "reg:tweedie",
  "binary:logistic",
] as const;

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
