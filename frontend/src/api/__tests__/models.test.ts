import { describe, expect, it } from "vitest";

import {
  boundCentral,
  ebmFit,
  gbmFit,
  gbmSpec,
  intervalWidth,
  relativityInterval,
  spansZero,
  type Coefficient,
  type Model,
} from "../models";

function coefficient(over: Partial<Coefficient> = {}): Coefficient {
  return {
    term: "t", estimate: 0.5, std_error: 0.1, z: 5, p_value: 0,
    ci_95: [0.3, 0.7], relativity: 1.65, ...over,
  } as Coefficient;
}

describe("reading a coefficient", () => {
  it("measures an interval's width", () => {
    expect(intervalWidth(coefficient())).toBeCloseTo(0.4, 10);
  });

  it("knows an interval that spans zero from one that does not", () => {
    // The distinction the screen marks: not distinguished from no effect at all.
    expect(spansZero(coefficient({ ci_95: [-0.1, 0.9] }))).toBe(true);
    expect(spansZero(coefficient({ ci_95: [0.3, 0.7] }))).toBe(false);
    // A boundary case: an interval touching zero has not excluded it.
    expect(spansZero(coefficient({ ci_95: [0, 0.9] }))).toBe(true);
  });

  it("exponentiates the interval for a log link, because that is what the table shows", () => {
    // A relativity's interval is not the coefficient's interval — reading one as the other
    // understates the spread of every relativity above 1.
    const [low, high] = relativityInterval(coefficient({ ci_95: [0, Math.LN2] }));
    expect(low).toBeCloseTo(1.0, 10);
    expect(high).toBeCloseTo(2.0, 10);
  });
});

const GBM = {
  id: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
  model_family_slug: "motor-ad-frequency",
  version: 7,
  status: "fitted",
  spec_hash: "v10:sha256:abc",
  dataset_version_id: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
  spec: {
    model_type: "lightgbm",
    model_family_slug: "motor-ad-frequency",
    dataset_version_id: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
    response_column: "ad_claim_count",
    objective: { kind: "builtin", name: "count:poisson" },
    categorical_handling: "native",
    interval_for: null,
  },
  fit_result: {
    model_type: "lightgbm",
    booster_blob: { sha256: "a".repeat(64), bytes: 184320, media_type: "text/plain" },
    booster_format: "lightgbm_text",
    feature_order: ["driver_age_banded"],
    base_margin: { kind: "log_column", column: "exposure_years" },
    best_iteration: 184,
    fit_seconds: 41.7,
  },
  flags: [],
} as unknown as Model;

describe("the model arm narrowers", () => {
  it("treats both boosters as one GBM arm", () => {
    // `GbmSpec.model_type` is `xgboost` or `lightgbm`: the backend IS the discriminator
    // (`02` §4.4, amended 2026-08-17). A narrower that checks only the first renders an
    // empty page for every LightGBM model, and it looks like a data problem.
    expect(gbmSpec(GBM)?.model_type).toBe("lightgbm");
    expect(gbmFit(GBM)?.booster_format).toBe("lightgbm_text");
    expect(ebmFit(GBM)).toBeNull();
  });

  it("locates the model a bound bounds, from the bound alone", () => {
    // FR-MODEL-78: a bound shares its central model's Model Family, and the backend refuses
    // a mismatch by name (MODEL_INTERVAL_PAIR_INVALID). The slug on the bound IS the central
    // model's slug — read off the contract, not derived from a naming convention.
    const bound = {
      ...GBM,
      spec: {
        ...GBM.spec,
        interval_for: { model_id: GBM.id, model_version: 7, alpha: 0.05 },
      },
    } as unknown as Model;
    expect(boundCentral(bound)).toEqual({
      slug: "motor-ad-frequency",
      version: 7,
      alpha: 0.05,
    });
    expect(boundCentral(GBM)).toBeNull();
  });
});
