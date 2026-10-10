// The structural diff overlay (FR-219): marks as text, the panel, the 404 and the clear.
import userEvent from "@testing-library/user-event";
import { render, screen, within } from "@testing-library/vue";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";

import { ProblemError } from "@/api/problem";
import type { AlgorithmDiff } from "@/api/ratingAlgorithms";

import DagDesigner from "../DagDesigner.vue";
import DiffOverlay from "../DiffOverlay.vue";
import { valid } from "./fixtures";

const api = vi.hoisted(() => ({
  getAlgorithmDiff: vi.fn(),
  validateRatingAlgorithm: vi.fn(),
  saveRatingAlgorithm: vi.fn(),
}));
vi.mock("@/api/ratingAlgorithms", () => api);

beforeAll(() => {
  globalThis.ResizeObserver ??= class {
    observe(): void {}
    unobserve(): void {}
    disconnect(): void {}
  };
});

const [added, changed] = [valid.steps[1]?.step_id ?? "", valid.steps[2]?.step_id ?? ""];
const DIFF: AlgorithmDiff = {
  added_steps: [added],
  removed_steps: ["s_old"],
  changed_steps: [{ step_id: changed, field: "rate_table_ref", before: "a", after: "b" }],
  repointed_tables: [
    {
      step_id: changed,
      field: "rate_table_ref",
      before: "rate_table:motor-expense@2",
      after: "rate_table:motor-expense@3",
    },
  ],
  input_contract_changed: false,
  outputs_changed: false,
};

beforeEach(() => {
  api.getAlgorithmDiff.mockReset();
  api.validateRatingAlgorithm.mockResolvedValue({ issues: [] });
});

describe("DiffOverlay", () => {
  it("defaults to the previous version and is absent for version 1", () => {
    const { unmount } = render(DiffOverlay, { props: { slug: "motor-gb", version: 3 } });
    expect(screen.getByLabelText("Compare with version")).toHaveValue(2);
    unmount();
    render(DiffOverlay, { props: { slug: "motor-gb", version: 1 } });
    expect(screen.queryByLabelText("Compare with version")).toBeNull();
  });

  it("lists removed steps and re-pointed tables in the panel", async () => {
    api.getAlgorithmDiff.mockResolvedValue(DIFF);
    const { emitted } = render(DiffOverlay, { props: { slug: "motor-gb", version: 3 } });
    await userEvent.click(screen.getByRole("button", { name: "Compare" }));
    const panel = await screen.findByRole("region", { name: "Differences" });
    expect(within(panel).getByText("s_old")).toBeInTheDocument();
    expect(within(panel).getByText(/rate_table:motor-expense@2 → rate_table:motor-expense@3/)).toBeInTheDocument();
    expect(api.getAlgorithmDiff).toHaveBeenCalledWith("motor-gb", 3, 2);
    expect(emitted().diff?.at(-1)).toEqual([DIFF]);
  });

  it("says the version was not found on a 404", async () => {
    api.getAlgorithmDiff.mockRejectedValue(
      new ProblemError({
        type: "about:blank",
        title: "Not found",
        status: 404,
        code: "NOT_FOUND",
        errors: [],
      }),
    );
    render(DiffOverlay, { props: { slug: "motor-gb", version: 3 } });
    await userEvent.click(screen.getByRole("button", { name: "Compare" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Version not found");
  });

  it("emits null when the input is cleared", async () => {
    const { emitted } = render(DiffOverlay, { props: { slug: "motor-gb", version: 3 } });
    await userEvent.clear(screen.getByLabelText("Compare with version"));
    expect(emitted().diff?.at(-1)).toEqual([null]);
  });
});

describe("the designer with the overlay", () => {
  const props = {
    draft: { ...valid, version: 3 },
    versionMode: "exact" as const,
    rateTablePins: ["rate_table:motor-expense@3"],
  };

  it("marks added and changed nodes as text, and removes every marker when cleared", async () => {
    api.getAlgorithmDiff.mockResolvedValue(DIFF);
    render(DagDesigner, { props });
    await userEvent.click(screen.getByRole("button", { name: "Compare" }));
    const addedNode = await screen.findByLabelText(new RegExp(`\\(${added}\\)`));
    expect(await within(addedNode).findByText("added")).toBeInTheDocument();
    const changedNode = screen.getByLabelText(new RegExp(`\\(${changed}\\)`));
    expect(within(changedNode).getByText("changed")).toBeInTheDocument();

    await userEvent.clear(screen.getByLabelText("Compare with version"));
    expect(screen.queryByText("added")).toBeNull();
    expect(screen.queryByText("changed")).toBeNull();
  });
});
