import { render, screen, waitFor, within } from "@testing-library/vue";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { Model } from "@/api/models";

import ModelListView from "../ModelListView.vue";

const listModels = vi.fn();

vi.mock("@/api/models", async (importOriginal) => ({
  ...(await importOriginal<object>()),
  listModels: () => listModels(),
}));

function model(over: Partial<Model> = {}): Model {
  return {
    id: "01a00500-0000-7000-8000-000000000001",
    dataset_version_id: "01a00495-58d0-71f8-a039-cd4c45337960",
    model_family_slug: "motor-ad-frequency",
    version: 7,
    status: "approved",
    ...over,
  } as Model;
}

afterEach(() => vi.clearAllMocks());

const stubs = {
  RouterLink: { props: ["to"], template: '<a :href="to"><slot /></a>' },
};

describe("the model list", () => {
  it("links each model row to its detail route with its version", async () => {
    listModels.mockResolvedValue({
      items: [
        model(),
        model({ id: "m2", model_family_slug: "freq-poisson", version: 3 }),
      ],
      truncated: false,
    });
    render(ModelListView, { global: { stubs } });

    // The table renders only once the rows are present, so waiting on it is
    // waiting on the fetch. `findAllByRole("link")` alone resolves on the two
    // header links before the mock promise lands.
    const rows = within(await screen.findByRole("table")).getAllByRole("link");
    expect(
      rows.some((row) => row.getAttribute("href") === "/models/motor-ad-frequency?version=7"),
    ).toBe(true);
    expect(rows.some((row) => row.getAttribute("href") === "/models/freq-poisson?version=3")).toBe(
      true,
    );
  });

  it("offers the two header actions: a new model and a comparison", async () => {
    listModels.mockResolvedValue({ items: [], truncated: false });
    render(ModelListView, { global: { stubs } });

    const newLink = await screen.findByRole("link", { name: "New model" });
    expect(newLink.getAttribute("href")).toBe("/models/new");
    const compare = screen.getByRole("link", { name: "Compare" });
    expect(compare.getAttribute("href")).toBe("/models/compare");
  });

  it("says when nothing has been fitted yet", async () => {
    listModels.mockResolvedValue({ items: [], truncated: false });
    render(ModelListView, { global: { stubs } });

    await waitFor(() =>
      expect(screen.getByText(/no models yet/i)).toBeInTheDocument(),
    );
  });
});
