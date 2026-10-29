// RL-1835 acceptance: the designer draws, marks, lists and edits sub-graph mounts.
import userEvent from "@testing-library/user-event";
import { render, screen, waitFor, within } from "@testing-library/vue";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";

import type { RatingAlgorithmDraft } from "@/api/ratingAlgorithms";

import DagDesigner from "../DagDesigner.vue";
import { FEES, FRAGMENT, PINS, REFUND, withMounts } from "./mountFixtures";

const api = vi.hoisted(() => ({
  validateRatingAlgorithm: vi.fn(),
  saveRatingAlgorithm: vi.fn(),
  getAlgorithmDiff: vi.fn(),
  getSubGraph: vi.fn(),
}));
vi.mock("@/api/ratingAlgorithms", () => api);
vi.mock("@/api/subGraphs", () => api);

beforeAll(() => {
  globalThis.ResizeObserver ??= class {
    observe(): void {}
    unobserve(): void {}
    disconnect(): void {}
  };
});

beforeEach(() => {
  for (const fn of Object.values(api)) fn.mockReset();
  api.validateRatingAlgorithm.mockResolvedValue({ issues: [] });
  api.getSubGraph.mockResolvedValue(FRAGMENT);
});

const props = {
  draft: withMounts,
  versionMode: "exact" as const,
  rateTablePins: [],
  subGraphPins: PINS,
};
const node = (id: string): HTMLElement => {
  const found = document.querySelector<HTMLElement>(`.vue-flow__node[data-id="${id}"]`);
  if (found === null) throw new Error(`no node ${id}`);
  return found;
};
const lastDraft = (emitted: Record<string, unknown[][]>): RatingAlgorithmDraft =>
  (emitted["update:draft"] ?? []).at(-1)?.[0] as RatingAlgorithmDraft;

describe("sub-graph mounts on the canvas (RL-1835 (i))", () => {
  it("draws one node per mount, its id the mount_point", async () => {
    render(DagDesigner, { props });
    await screen.findByLabelText(/sub-graph mount m_fees/);
    expect(node("m_fees")).toBeInTheDocument();
    expect(node("m_refund")).toBeInTheDocument();
  });

  it("marks the cancellation-only mount with its badge text and a dashed border, and no other", async () => {
    render(DagDesigner, { props });
    await screen.findByLabelText(/sub-graph mount m_refund/);
    const purpose = within(node("m_refund"));
    expect(purpose.getByText("Cancellation only")).toBeInTheDocument();
    expect(purpose.getByLabelText(/sub-graph mount m_refund/).className).toContain("border-dashed");
    const plain = within(node("m_fees"));
    expect(plain.queryByText(/only|MTA/)).toBeNull();
    expect(plain.getByLabelText(/sub-graph mount m_fees/).className).not.toContain("border-dashed");
  });

  it("draws the conditional mount's edges dashed and the unconditional mount's solid", async () => {
    render(DagDesigner, { props });
    await screen.findByLabelText(/sub-graph mount m_refund/);
    const dash = (target: string): string | null => {
      const edge = document.querySelector<SVGElement>(`.vue-flow__edge[data-id*="${target}"] path`);
      return edge === null ? null : (edge.style.strokeDasharray ?? "");
    };
    expect(dash("m_refund")).toBe("6 4");
    expect(dash("m_fees")).toBe("");
  });

  it("shows a validate-route issue located at a mount_point on that node", async () => {
    api.validateRatingAlgorithm.mockResolvedValue({
      issues: [{ code: "GRAPH_CYCLE", message: "m_refund closes a cycle", step_id: "m_refund" }],
    });
    render(DagDesigner, { props });
    await screen.findByLabelText(/sub-graph mount m_refund/);
    expect(await within(node("m_refund")).findByText("m_refund closes a cycle")).toBeInTheDocument();
    expect(within(node("m_fees")).queryByText("m_refund closes a cycle")).toBeNull();
  });

  it("warns, in text, on a mount whose version the Rating Version does not pin", async () => {
    render(DagDesigner, { props: { ...props, subGraphPins: [FEES.ref] } });
    await screen.findByLabelText(/sub-graph mount m_refund/);
    expect(within(node("m_refund")).getByText(/not pinned by this Rating Version/)).toBeInTheDocument();
    expect(within(node("m_fees")).queryByText(/not pinned/)).toBeNull();
  });

  it("marks only the mount a sub_graph_mounts entry names, from the diff", async () => {
    api.getAlgorithmDiff.mockResolvedValue({
      added_steps: [],
      removed_steps: [],
      changed_steps: [],
      sub_graph_mounts: [{ mount_point: "m_refund", before: null, after: REFUND.ref }],
      input_contract_changed: false,
      outputs_changed: false,
    });
    render(DagDesigner, { props: { ...props, draft: { ...withMounts, version: 3 } } });
    await userEvent.click(screen.getByRole("button", { name: "Compare" }));
    expect(await within(node("m_refund")).findByText("added")).toBeInTheDocument();
    expect(within(node("m_fees")).queryByText("added")).toBeNull();
    expect(within(node("m_fees")).queryByText("changed")).toBeNull();
  });
});

describe("sub-graph mounts by keyboard and in the inspector (RL-1835 (i) 5-6, (iii))", () => {
  it("lists each mount in the node navigator", () => {
    render(DagDesigner, { props });
    const ids = screen.getAllByRole("option").map((o) => o.id);
    expect(ids).toContain("nav-m_fees");
    expect(ids).toContain("nav-m_refund");
  });

  it("opens the mount's inspector from the navigator with Enter", async () => {
    render(DagDesigner, { props });
    await userEvent.click(screen.getByRole("listbox", { name: "Steps in graph order" }));
    await userEvent.keyboard("m_refund{Enter}");
    expect(await screen.findByRole("form", { name: "Inspector for m_refund" })).toBeInTheDocument();
  });

  it("removes a mount after confirmation, leaving the steps", async () => {
    const { emitted } = render(DagDesigner, { props });
    await userEvent.click(screen.getByRole("listbox", { name: "Steps in graph order" }));
    await userEvent.keyboard("m_fees{Delete}");
    await userEvent.click(screen.getByRole("button", { name: "Remove mount" }));
    const draft = lastDraft(emitted() as Record<string, unknown[][]>);
    expect(draft.sub_graphs?.map((m) => m.mount_point)).toEqual(["m_refund"]);
    expect(draft.steps).toHaveLength(withMounts.steps.length);
  });

  it("adds a mount of the first pinned version, new and selected", async () => {
    const { emitted } = render(DagDesigner, { props: { ...props, draft: { ...withMounts, sub_graphs: [] } } });
    await userEvent.click(screen.getByRole("button", { name: "Add sub-graph mount" }));
    const draft = lastDraft(emitted() as Record<string, unknown[][]>);
    expect(draft.sub_graphs).toEqual([{ ref: PINS[0], mount_point: "m_new_1", inputs: {}, outputs: {} }]);
  });

  it("disables adding a mount, with a text reason, when the Rating Version pins no sub-graph", () => {
    render(DagDesigner, { props: { ...props, subGraphPins: [] } });
    expect(screen.getByRole("button", { name: "Add sub-graph mount" })).toBeDisabled();
    expect(screen.getByText("This Rating Version pins no sub-graph")).toBeInTheDocument();
  });

  it("saves an edited mount into sub_graphs and leaves the other mount as it was", async () => {
    const { emitted } = render(DagDesigner, { props });
    await userEvent.click(screen.getByRole("listbox", { name: "Steps in graph order" }));
    await userEvent.keyboard("m_refund{Enter}");
    await userEvent.click(await screen.findByLabelText("mid_term_adjustment"));
    await waitFor(() => {
      const draft = lastDraft(emitted() as Record<string, unknown[][]>);
      expect(draft.sub_graphs?.[1]?.purposes).toEqual(["mid_term_adjustment", "cancellation"]);
      expect(draft.sub_graphs?.[0]).toEqual(FEES);
    });
  });
});
