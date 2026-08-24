import { describe, expect, it } from "vitest";

import { comparisonIdFromJob, leaderState, parseModelRef } from "@/api/comparisons";
import type { ComparisonMetric } from "@/api/comparisons";
import type { Job } from "@/api/jobs";

// A Job with only the fields these helpers read. Annotated `Partial<Job>` and cast at the
// call, rather than `as Job`, so a required field added to the contract does not silently
// pass here — the cast is at one place and says exactly what it is hiding.
function jobWith(result: Job["result"]): Job {
  return { result } as Job;
}

describe("comparisonIdFromJob", () => {
  // `backend/src/app/worker/model_handlers.py:786` — the ref is `model_comparison:{uuid}`,
  // NOT `comparison:{uuid}` and NOT an ID-3 `{type}:{slug}@{version}` reference.
  // `model_comparison` is not in `refs.py`'s ARTIFACT_TYPES and there is no version segment.
  it("reads the id out of a model_comparison ref", () => {
    const job = jobWith({
      kind: "artifact",
      ref: "model_comparison:0e3f7a1c-1111-4222-8333-444455556666",
    });
    expect(comparisonIdFromJob(job)).toBe("0e3f7a1c-1111-4222-8333-444455556666");
  });

  // `model_handlers.py:554` emits `model:{uuid}` for a fit job. A prefix check loose enough
  // to accept that would hand the view a model id and a 404 it could not explain.
  it("refuses every other artifact ref, and a job with no result", () => {
    expect(
      comparisonIdFromJob(
        jobWith({ kind: "artifact", ref: "model:0e3f7a1c-1111-4222-8333-444455556666" }),
      ),
    ).toBeNull();
    expect(
      comparisonIdFromJob(
        jobWith({ kind: "artifact", ref: "backtest:0e3f7a1c-1111-4222-8333-444455556666" }),
      ),
    ).toBeNull();
    expect(comparisonIdFromJob(jobWith({ kind: "none", ref: null }))).toBeNull();
    expect(comparisonIdFromJob(jobWith(null))).toBeNull();
  });
});

describe("parseModelRef", () => {
  // `packages/model-schema/src/model_schema/refs.py:30-43`. `ComparisonValue.model_ref` is a
  // bare `str` with no validator, so this parse can fail on a well-formed artifact and the
  // caller renders the raw string instead.
  it("splits an ID-3 model ref into slug and version", () => {
    expect(parseModelRef("model:motor-ad-frequency@7")).toEqual({
      slug: "motor-ad-frequency",
      version: 7,
    });
  });

  it("returns null for anything the pattern does not accept", () => {
    expect(parseModelRef("model:motor-ad-frequency")).toBeNull(); // no version
    expect(parseModelRef("model:motor-ad-frequency@0")).toBeNull(); // versions start at 1
    expect(parseModelRef("dataset:motor@3")).toBeNull(); // not a model
    expect(parseModelRef("model:Motor-AD@7")).toBeNull(); // slugs are lower-case
    expect(parseModelRef("model:0e3f7a1c-1111-4222-8333-444455556666")).toBeNull(); // a JobResult ref
  });
});

describe("leaderState", () => {
  const metric = (
    direction: ComparisonMetric["direction"],
    leader: string | null,
  ): ComparisonMetric => ({
    metric: "gini_normalised",
    weighting: "exposure",
    direction,
    values: [
      { model_ref: "model:a@1", value: 0.41 },
      { model_ref: "model:b@1", value: 0.43 },
    ],
    leader,
  });

  it("names the leader and the models behind it", () => {
    expect(leaderState(metric("higher_is_better", "model:b@1"), "model:b@1")).toBe("leader");
    expect(leaderState(metric("higher_is_better", "model:b@1"), "model:a@1")).toBe("behind");
  });

  // `02` §4.11: leader is null "where the metric does not order **or the models tie** — a
  // winner chosen by tie-break is one the data did not choose". Two different facts; a view
  // that renders both as an empty cell loses one of them.
  it("distinguishes a tie from a metric that does not order", () => {
    expect(leaderState(metric("higher_is_better", null), "model:a@1")).toBe("tied");
    expect(leaderState(metric("closer_to_one_is_better", null), "model:a@1")).toBe("tied");
    expect(leaderState(metric("not_ordered", null), "model:a@1")).toBe("unranked");
  });
});
