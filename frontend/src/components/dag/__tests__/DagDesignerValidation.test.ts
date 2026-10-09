// Live validation on the real Vue Flow (03 FR 9445, FR-24): the server's issues are shown on
// the node they locate, before any save. The route is mocked; no rule is evaluated here.
import { render, screen, within } from "@testing-library/vue";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";

import DagDesigner from "../DagDesigner.vue";
import { valid } from "./fixtures";

const api = vi.hoisted(() => ({ validateRatingAlgorithm: vi.fn(), saveRatingAlgorithm: vi.fn() }));
vi.mock("@/api/ratingAlgorithms", () => api);

beforeAll(() => {
  globalThis.ResizeObserver ??= class {
    observe(): void {}
    unobserve(): void {}
    disconnect(): void {}
  };
});

const props = { draft: valid, versionMode: "exact" as const, rateTablePins: ["rate_table:motor-expense@3"] };
const target = valid.steps[1]?.step_id ?? "";

beforeEach(() => {
  api.validateRatingAlgorithm.mockReset();
  api.saveRatingAlgorithm.mockReset();
});

describe("live graph validation in the designer", () => {
  it("FR 9445: an unresolved reference is shown on its node before save", async () => {
    api.validateRatingAlgorithm.mockResolvedValue({
      issues: [
        {
          code: "RATING_GRAPH_UNRESOLVED_REF",
          message: "step consumes a name nothing produces",
          step_id: target,
          field: "consumes",
        },
      ],
    });
    render(DagDesigner, { props });
    const node = await screen.findByLabelText(new RegExp(`\\(${target}\\), 1 issue$`));
    expect(within(node).getByText("step consumes a name nothing produces")).toBeInTheDocument();
    expect(api.saveRatingAlgorithm).not.toHaveBeenCalled();
  });

  it("shows a graph-level issue in the status panel and announces the count politely", async () => {
    api.validateRatingAlgorithm.mockResolvedValue({
      issues: [
        { code: "OUTPUT_UNPRODUCED", message: "output premium has no output step", step_id: null, field: null },
        { code: "RATING_GRAPH_ORPHAN", message: "step is not reachable", step_id: target, field: null },
      ],
    });
    render(DagDesigner, { props });
    const panel = await screen.findByRole("status", { name: "Graph issues" });
    expect(await within(panel).findByText(/output premium has no output step/)).toBeInTheDocument();
    const live = await screen.findByText("2 issues");
    expect(live).toHaveAttribute("aria-live", "polite");
  });

  it("puts the issue count in the navigator option's accessible name", async () => {
    api.validateRatingAlgorithm.mockResolvedValue({
      issues: [{ code: "X", message: "bad", step_id: target, field: null }],
    });
    render(DagDesigner, { props });
    const option = await screen.findByRole("option", { name: new RegExp(`^${target} .*, 1 issue$`) });
    expect(option).toBeInTheDocument();
  });
});
