import { describe, expect, it } from "vitest";

import type { Factor, Model } from "@/api/models";
import { requiredColumns } from "@/api/predictionInputs";

const DATASET = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb";

function factor(id: string, slug: string, extra: Partial<Factor> = {}): Factor {
  return {
    id,
    slug,
    dataset_id: DATASET,
    version: 1,
    type: "identity",
    source_columns: [slug],
    operand_factor_ids: [],
    base_level_method: "largest_exposure",
    base_level: null,
    banding_id: null,
    grouping_id: null,
    intent: "rating",
    monotonic_direction: null,
    monotonic_rationale: null,
    prohibited: false,
    prohibited_reason: null,
    ...extra,
  } as Factor;
}

function glm(factorIds: string[], offset: Model["spec"]["offset"]): Model {
  return {
    id: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    model_family_slug: "motor-ad-frequency",
    version: 3,
    status: "fitted",
    spec_hash: "v10:sha256:abc",
    dataset_version_id: DATASET,
    spec: {
      model_type: "glm",
      model_family_slug: "motor-ad-frequency",
      dataset_version_id: DATASET,
      response_column: "ad_claim_count",
      family: "poisson",
      link: "log",
      factors: factorIds,
      offset,
      weight: { kind: "none" },
      loss_treatment: { kind: "none" },
      seed: 0,
    },
  } as unknown as Model;
}

function byId(...factors: Factor[]): Map<string, Factor> {
  return new Map(factors.map((f) => [f.id, f]));
}

describe("requiredColumns", () => {
  it("reads columns off the factors, not off the pinned ids", () => {
    // `GlmSpec.factors` is an array of uuid. The ids are not column names, and a form built
    // from them would ask the user for a uuid.
    const age = factor("f1", "driver_age", { source_columns: ["driver_age_years"] });
    const result = requiredColumns(glm(["f1"], { kind: "none" }), byId(age));

    expect(result.columns).toEqual(["driver_age_years"]);
    expect(result.unresolvedFactorIds).toEqual([]);
  });

  it("expands an interaction's operands one level", () => {
    // An `interaction` Factor has empty `source_columns` by validated invariant, and its
    // operands are NOT in `spec.factors`. Without this expansion the form omits real
    // columns and every submission fails with MODEL_TERM_UNRESOLVED.
    const age = factor("f1", "driver_age", { source_columns: ["driver_age_years"] });
    const area = factor("f2", "area", { source_columns: ["area_code"] });
    const cross = factor("f3", "age_x_area", {
      type: "interaction",
      source_columns: [],
      operand_factor_ids: ["f1", "f2"],
    });

    const result = requiredColumns(glm(["f3"], { kind: "none" }), byId(age, area, cross));

    expect(result.columns).toEqual(["area_code", "driver_age_years"]);
  });

  it("includes an explicit offset column", () => {
    const age = factor("f1", "driver_age", { source_columns: ["driver_age_years"] });
    const result = requiredColumns(
      glm(["f1"], { kind: "log_column", column: "exposure_years" }),
      byId(age),
    );

    expect(result.columns).toEqual(["driver_age_years", "exposure_years"]);
  });

  it("reports the offset model ref rather than silently omitting its columns", () => {
    // The backend scores the referenced model on the CALLER's frame, so its factor columns
    // must be present too. Returning the ref is how the view knows to fetch and union.
    const age = factor("f1", "driver_age", { source_columns: ["driver_age_years"] });
    const result = requiredColumns(
      glm(["f1"], { kind: "model", offset_model_ref: "model:base-burning-cost@4" }),
      byId(age),
    );

    expect(result.offsetModelRef).toEqual({ slug: "base-burning-cost", version: 4 });
  });

  it("reports a pinned factor it cannot resolve instead of dropping it", () => {
    // A form quietly missing a column is the failure this whole module exists to prevent.
    const result = requiredColumns(glm(["f1", "f9"], { kind: "none" }), byId(factor("f1", "a")));

    expect(result.columns).toEqual(["a"]);
    expect(result.unresolvedFactorIds).toEqual(["f9"]);
  });
});
