// Mounts the REAL @vue-flow/core (the Vue 3 smoke proof of the pnpm-workspace ruling, condition 2):
// VueFlow is not stubbed. happy-dom has no layout engine, so only what Vue Flow renders without
// measuring is asserted here; the canvas's pan and zoom are measured in Task 11, not unit-tested.
import userEvent from "@testing-library/user-event";
import { render, screen } from "@testing-library/vue";
import { beforeAll, describe, expect, it } from "vitest";

import type { RatingAlgorithmDraft } from "@/api/ratingAlgorithms";

import DagDesigner from "../DagDesigner.vue";
import { valid } from "./fixtures";

beforeAll(() => {
  // A browser API happy-dom lacks; Vue Flow observes its pane with it.
  globalThis.ResizeObserver ??= class {
    observe(): void {}
    unobserve(): void {}
    disconnect(): void {}
  };
});

const props = { draft: valid, versionMode: "exact" as const, rateTablePins: ["rate_table:motor-expense@3"] };

function lastDraft(emitted: Record<string, unknown[][]>): RatingAlgorithmDraft {
  return (emitted["update:draft"] ?? []).at(-1)?.[0] as RatingAlgorithmDraft;
}

describe("the DAG designer on the real Vue Flow", () => {
  it("draws one node per step, each carrying its type, label and step_id", async () => {
    render(DagDesigner, { props });
    for (const step of valid.steps) {
      expect(
        await screen.findByLabelText(`${step.type} step ${step.label} (${step.step_id})`),
      ).toBeInTheDocument();
    }
  });

  it("opens the inspector for the step the navigator selects with Enter", async () => {
    render(DagDesigner, { props });
    await userEvent.click(screen.getByRole("listbox", { name: "Steps in graph order" }));
    await userEvent.keyboard("s_area{Enter}");
    expect(await screen.findByRole("form", { name: "Inspector for s_area" })).toBeInTheDocument();
  });

  it("emits an edited draft and leaves the other steps as they were", async () => {
    const { emitted } = render(DagDesigner, { props });
    await userEvent.click(screen.getByRole("listbox", { name: "Steps in graph order" }));
    await userEvent.keyboard("s_area{Enter}");
    await userEvent.type(await screen.findByLabelText("Label"), "!");
    const draft = lastDraft(emitted() as Record<string, unknown[][]>);
    expect(draft.steps.find((s) => s.step_id === "s_area")?.label).toBe("Area!");
    expect(draft.steps).toHaveLength(valid.steps.length);
  });

  it("adds a step of the chosen type, new and selected, and removes one after confirmation", async () => {
    const { emitted } = render(DagDesigner, { props });
    await userEvent.selectOptions(screen.getByLabelText("Step type to add"), "constraint");
    await userEvent.click(screen.getByRole("button", { name: "Add step" }));
    const added = lastDraft(emitted() as Record<string, unknown[][]>);
    expect(added.steps).toHaveLength(valid.steps.length + 1);
    expect(added.steps.at(-1)?.type).toBe("constraint");

    await userEvent.click(screen.getByRole("listbox", { name: "Steps in graph order" }));
    await userEvent.keyboard("s_in_age{Delete}");
    await userEvent.click(screen.getByRole("button", { name: "Remove step" }));
    const removed = lastDraft(emitted() as Record<string, unknown[][]>);
    expect(removed.steps.map((s) => s.step_id)).not.toContain("s_in_age");
  });
});
