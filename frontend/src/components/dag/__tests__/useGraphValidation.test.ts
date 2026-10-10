import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { effectScope, nextTick, ref } from "vue";

import type { AlgorithmValidationReport, RatingAlgorithmDraft } from "@/api/ratingAlgorithms";

import { useGraphValidation } from "../useGraphValidation";
import { valid } from "./fixtures";

const validate = vi.hoisted(() => vi.fn());
vi.mock("@/api/ratingAlgorithms", () => ({ validateRatingAlgorithm: validate }));

const issue = (step_id: string | null, code = "SOME_CODE") => ({
  code,
  message: `m-${code}`,
  step_id,
  field: null,
});

function setup(delay = 400) {
  const draft = ref<RatingAlgorithmDraft>(valid);
  const scope = effectScope();
  const api = scope.run(() => useGraphValidation(draft, delay));
  if (!api) throw new Error("scope did not run");
  const edit = (label: string) => {
    draft.value = { ...draft.value, slug: label };
  };
  return { api, edit, scope };
}

beforeEach(() => {
  vi.useFakeTimers();
  validate.mockReset();
  validate.mockResolvedValue({ issues: [] } satisfies AlgorithmValidationReport);
});
afterEach(() => vi.useRealTimers());

describe("useGraphValidation (FR-1607)", () => {
  it("makes one call for three changes inside the debounce window", async () => {
    const { edit, scope } = setup();
    edit("a");
    await nextTick();
    await vi.advanceTimersByTimeAsync(100);
    edit("b");
    await nextTick();
    await vi.advanceTimersByTimeAsync(100);
    edit("c");
    await nextTick();
    await vi.advanceTimersByTimeAsync(400);
    expect(validate).toHaveBeenCalledTimes(1);
    expect(validate.mock.calls[0]?.[0].slug).toBe("c");
    scope.stop();
  });

  it("aborts the call still pending when the draft changes again", async () => {
    validate.mockImplementation(() => new Promise(() => {}));
    const { edit, scope } = setup();
    await vi.advanceTimersByTimeAsync(400);
    const first = validate.mock.calls[0]?.[1] as AbortSignal;
    expect(first.aborted).toBe(false);
    edit("next");
    await nextTick();
    expect(first.aborted).toBe(true);
    scope.stop();
  });

  it("does not let a late older response replace a newer one", async () => {
    let releaseFirst: (r: AlgorithmValidationReport) => void = () => {};
    validate.mockImplementationOnce(
      () => new Promise<AlgorithmValidationReport>((resolve) => (releaseFirst = resolve)),
    );
    validate.mockResolvedValueOnce({ issues: [issue("s_b", "NEW")] });
    const { api, edit, scope } = setup();
    await vi.advanceTimersByTimeAsync(400);
    edit("next");
    await nextTick();
    await vi.advanceTimersByTimeAsync(400);
    expect(api.issues.value.map((i) => i.code)).toEqual(["NEW"]);
    releaseFirst({ issues: [issue("s_a", "OLD")] });
    await vi.advanceTimersByTimeAsync(0);
    expect(api.issues.value.map((i) => i.code)).toEqual(["NEW"]);
    scope.stop();
  });

  it("groups located issues by step and keeps the unlocated as graph-level", async () => {
    validate.mockResolvedValue({
      issues: [issue("s_b", "A"), issue("s_b", "B"), issue(null, "G")],
    });
    const { api, scope } = setup();
    await vi.advanceTimersByTimeAsync(400);
    expect(api.byStep.value.get("s_b")?.map((i) => i.code)).toEqual(["A", "B"]);
    expect(api.graphLevel.value.map((i) => i.code)).toEqual(["G"]);
    expect(api.pending.value).toBe(false);
    scope.stop();
  });
});
