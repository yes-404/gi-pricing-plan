import { render, screen, waitFor } from "@testing-library/vue";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { Model } from "@/api/models";

import ModelSelector from "../ModelSelector.vue";

const listModels = vi.fn();

vi.mock("@/api/models", async (importOriginal) => ({
  ...(await importOriginal<object>()),
  listModels: () => listModels(),
}));

function model(id: string, over: Partial<Model> = {}): Model {
  return {
    id,
    dataset_version_id: "v1",
    model_family_slug: `family-${id}`,
    version: 1,
    status: "fitted",
    ...over,
  } as Model;
}

function selector(props: Record<string, unknown> = {}) {
  return render(ModelSelector, {
    props: { datasetVersionId: "v1", ...props },
  });
}

const options = () =>
  screen.getAllByRole("option").map((o) => o.textContent?.trim() ?? "");

afterEach(() => vi.clearAllMocks());

describe("the model selector", () => {
  it("offers only models fitted on this dataset version", async () => {
    listModels.mockResolvedValue({
      items: [model("a"), model("b", { dataset_version_id: "other" })],
      truncated: false,
    });
    selector();

    await waitFor(() => expect(options().join(" ")).toContain("family-a"));
    expect(options().join(" ")).not.toContain("family-b");
  });

  it("defaults to the first, which is the route's most recent", async () => {
    // `Model` carries no timestamp — "most recent" is the route's `id.desc()` over UUIDv7.
    // So the default is positional, and this asserts the position rather than a date.
    listModels.mockResolvedValue({
      // Ids chosen so alphabetical order differs from the route's: a `sort` here would
      // put `a-older` first, so this test fails if the ordering is ever lost. With ids
      // that happen to sort into the same order, it would pass under exactly that defect.
      items: [model("z-newest"), model("a-older"), model("m-oldest")],
      truncated: false,
    });
    const { emitted } = selector();

    await waitFor(() => expect(emitted()["update:selected"]).toBeTruthy());
    const last = emitted()["update:selected"]?.at(-1) as [Model];
    expect(last[0].id).toBe("z-newest");
  });

  it("does not reorder what the route returned", async () => {
    // The defect this guards: any sort here would silently make the default an arbitrary
    // model, with nothing in the type system objecting.
    listModels.mockResolvedValue({
      items: [model("c"), model("a"), model("b")],
      truncated: false,
    });
    selector();

    await waitFor(() => expect(options().length).toBeGreaterThan(1));
    expect(options().slice(1).join(" ")).toMatch(/family-c.*family-a.*family-b/);
  });

  it("shows status in the label but never lets it pick the default", async () => {
    // Highest-status was the rejected alternative: it surfaces an older analysis while
    // newer work exists. Status informs the choice; it does not make it.
    listModels.mockResolvedValue({
      items: [model("newest", { status: "draft" }), model("older", { status: "approved" })],
      truncated: false,
    });
    const { emitted } = selector();

    await waitFor(() => expect(options().join(" ")).toContain("draft"));
    expect(options().join(" ")).toContain("approved");
    const last = emitted()["update:selected"]?.at(-1) as [Model];
    expect(last[0].id).toBe("newest");
  });

  it("honours a preselect that belongs to this version", async () => {
    listModels.mockResolvedValue({
      items: [model("newest"), model("wanted")],
      truncated: false,
    });
    const { emitted } = selector({ preselect: "wanted" });

    await waitFor(() => expect(emitted()["update:selected"]).toBeTruthy());
    const last = emitted()["update:selected"]?.at(-1) as [Model];
    expect(last[0].id).toBe("wanted");
  });

  it("ignores a preselect belonging to a different dataset version", async () => {
    // Honouring it would show an artifact built on different data, which is worse than
    // ignoring the hint.
    listModels.mockResolvedValue({
      items: [model("newest"), model("elsewhere", { dataset_version_id: "other" })],
      truncated: false,
    });
    const { emitted } = selector({ preselect: "elsewhere" });

    await waitFor(() => expect(emitted()["update:selected"]).toBeTruthy());
    const last = emitted()["update:selected"]?.at(-1) as [Model];
    expect(last[0].id).toBe("newest");
  });

  it("says the list may be incomplete rather than showing an honest-looking empty one", async () => {
    // OQ-611. An empty selector must be distinguishable from a walk that stopped.
    listModels.mockResolvedValue({ items: [], truncated: true });
    selector();

    expect(await screen.findByText(/may be incomplete/)).toBeInTheDocument();
    expect(screen.queryByText(/No models have been fitted/)).toBeNull();
  });

  it("says none were fitted only when the walk actually finished", async () => {
    listModels.mockResolvedValue({ items: [], truncated: false });
    selector();

    expect(await screen.findByText(/No models have been fitted/)).toBeInTheDocument();
  });

  it("survives a failed lookup without claiming the version has no models", async () => {
    const { ProblemError } = await import("@/api/problem");
    listModels.mockRejectedValue(new ProblemError({
      type: "t", title: "Boom", status: 500, code: "INTERNAL", errors: [],
    }));
    selector();

    expect(await screen.findByText(/could not be loaded/)).toBeInTheDocument();
    expect(screen.queryByText(/No models have been fitted/)).toBeNull();
  });
});
