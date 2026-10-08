import userEvent from "@testing-library/user-event";
import { render, screen } from "@testing-library/vue";
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from "vitest";

import { ProblemError } from "@/api/problem";
import { valid } from "@/components/dag/__tests__/fixtures";

import RatingDesignView from "../RatingDesignView.vue";

const getRatingVersionByRef = vi.fn();
const getRatingAlgorithm = vi.fn();
const saveRatingAlgorithm = vi.fn();

vi.mock("@/api/ratingVersions", () => ({
  getRatingVersionByRef: (...args: unknown[]) => getRatingVersionByRef(...args),
}));
vi.mock("@/api/ratingAlgorithms", () => ({
  getRatingAlgorithm: (...args: unknown[]) => getRatingAlgorithm(...args),
  saveRatingAlgorithm: (...args: unknown[]) => saveRatingAlgorithm(...args),
}));

beforeAll(() => {
  // A browser API happy-dom lacks (Vue Flow itself is NOT stubbed here).
  globalThis.ResizeObserver ??= class {
    observe(): void {}
    unobserve(): void {}
    disconnect(): void {}
  };
});

const RATING = {
  id: "01a04394-338b-7651-9e42-c73ee70396f8",
  workspace_id: "01a04394-0000-7000-8000-000000000001",
  slug: "fremtpl2-demo",
  version: 1,
  status: "draft",
  dataset_version_id: "01a04394-0000-7000-8000-000000000002",
  model_ref: "model:fremtpl2-glm@1",
  algorithm_ref: "rating_algorithm:motor-gb@1",
  model_reference_mode: "exact",
  pins: { rate_tables: ["rate_table:motor-expense@3"] },
  created_at: "2026-08-27T14:00:00Z",
  created_by: "01a04394-0000-7000-8000-000000000003",
  updated_at: "2026-08-27T14:05:00Z",
};

const props = { slug: "fremtpl2-demo", version: "1" };
const mounted = { global: { stubs: { RouterLink: { template: "<a><slot /></a>" } } } };

beforeEach(() => {
  getRatingVersionByRef.mockResolvedValue(RATING);
  getRatingAlgorithm.mockResolvedValue(structuredClone(valid));
  saveRatingAlgorithm.mockResolvedValue({ id: RATING.id, slug: "motor-gb", version: 2 });
});
afterEach(() => vi.clearAllMocks());

describe("the rating design view", () => {
  it("FR 1531: resolves the version by the slug and version of the URL", async () => {
    render(RatingDesignView, { props, ...mounted });
    await screen.findByLabelText("Algorithm version");
    expect(getRatingVersionByRef).toHaveBeenCalledWith("fremtpl2-demo", 1);
  });

  it("FR 1530: loads the algorithm the version pins, and draws one node per step", async () => {
    render(RatingDesignView, { props, ...mounted });
    for (const step of valid.steps) {
      expect(
        await screen.findByLabelText(`${step.type} step ${step.label} (${step.step_id})`),
      ).toBeInTheDocument();
    }
    expect(getRatingAlgorithm).toHaveBeenCalledWith("motor-gb", 1);
  });

  it("FR-212: saves the draft with the version the actuary set, pre-filled to the loaded one plus one", async () => {
    render(RatingDesignView, { props, ...mounted });
    const version = await screen.findByLabelText("Algorithm version");
    expect(version).toHaveValue(2);
    await userEvent.click(screen.getByRole("button", { name: "Save as new version" }));
    expect(await screen.findByText("Saved as motor-gb@2")).toBeInTheDocument();
    const [body, key] = saveRatingAlgorithm.mock.calls[0] as [Record<string, unknown>, string];
    expect(body["version"]).toBe(2);
    expect(body["slug"]).toBe("motor-gb");
    expect((body["steps"] as unknown[]).length).toBe(valid.steps.length);
    expect(key).toMatch(/^[0-9a-f-]{36}$/);
  });

  it("FR-212: shows a refused save with its code and detail, never a generic error", async () => {
    saveRatingAlgorithm.mockRejectedValue(
      new ProblemError({
        type: "about:blank",
        title: "Rating graph has a cycle",
        status: 422,
        code: "RATING_GRAPH_CYCLIC",
        detail: "Steps s_a and s_b consume each other.",
        errors: [],
      }),
    );
    render(RatingDesignView, { props, ...mounted });
    await screen.findByLabelText("Algorithm version");
    await userEvent.click(screen.getByRole("button", { name: "Save as new version" }));
    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("RATING_GRAPH_CYCLIC");
    expect(alert).toHaveTextContent("Steps s_a and s_b consume each other.");
  });

  it("shows a 409 for an existing version the same way", async () => {
    saveRatingAlgorithm.mockRejectedValue(
      new ProblemError({
        type: "about:blank",
        title: "Rating algorithm version already exists",
        status: 409,
        code: "VALIDATION_FAILED",
        detail: "motor-gb@2 already exists in this workspace.",
        errors: [],
      }),
    );
    render(RatingDesignView, { props, ...mounted });
    await screen.findByLabelText("Algorithm version");
    await userEvent.click(screen.getByRole("button", { name: "Save as new version" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("motor-gb@2 already exists");
  });

  it("blocks the save while a step has a required field empty", async () => {
    const broken = structuredClone(valid);
    const minprem = broken.steps.find((s) => s.step_id === "s_minprem");
    if (minprem?.type !== "constraint") throw new Error("fixture");
    minprem.reason_code = "";
    getRatingAlgorithm.mockResolvedValue(broken);
    render(RatingDesignView, { props, ...mounted });
    await screen.findByLabelText("Algorithm version");
    const save = screen.getByRole("button", { name: "Save as new version" });
    expect(save).toHaveAttribute("aria-disabled", "true");
    expect(save).toHaveAttribute("aria-describedby", "rd-problems");
    await userEvent.click(save);
    expect(saveRatingAlgorithm).not.toHaveBeenCalled();
    expect(screen.getByText(/s_minprem: reason_code is required \(FR-225\)/)).toBeInTheDocument();
  });

  it("DP-S2-3 (a): a version that pins no algorithm shows that, an empty canvas, and saves <slug>@1", async () => {
    getRatingVersionByRef.mockResolvedValue({ ...RATING, algorithm_ref: null });
    render(RatingDesignView, { props, ...mounted });
    expect(
      await screen.findByText(/This Rating Version pins no algorithm yet/),
    ).toHaveTextContent(
      "This Rating Version pins no algorithm yet. Saving creates fremtpl2-demo@1; pinning it to the version is not part of this view.",
    );
    expect(getRatingAlgorithm).not.toHaveBeenCalled();
    expect(screen.getByLabelText("Algorithm version")).toHaveValue(1);
    await userEvent.click(screen.getByRole("button", { name: "Save as new version" }));
    const [body] = saveRatingAlgorithm.mock.calls[0] as [Record<string, unknown>];
    expect(body).toMatchObject({ slug: "fremtpl2-demo", version: 1, steps: [] });
  });
});
