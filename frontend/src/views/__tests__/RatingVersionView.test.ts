import { render, screen } from "@testing-library/vue";
import { afterEach, describe, expect, it, vi } from "vitest";

import RatingVersionView from "../RatingVersionView.vue";

const getRatingVersion = vi.fn();

vi.mock("@/api/ratingVersions", () => ({
  getRatingVersion: (...args: unknown[]) => getRatingVersion(...args),
}));

const RATING = {
  id: "01a04394-338b-7651-9e42-c73ee70396f8",
  workspace_id: "01a04394-0000-7000-8000-000000000001",
  slug: "fremtpl2-demo",
  version: 1,
  status: "approved",
  dataset_version_id: "01a04394-0000-7000-8000-000000000002",
  model_ref: "model:fremtpl2-glm-7edfde@1",
  created_at: "2026-08-27T14:00:00Z",
  created_by: "01a04394-0000-7000-8000-000000000003",
  updated_at: "2026-08-27T14:05:00Z",
};

const props = { id: RATING.id };
const mounted = {
  global: {
    stubs: { RouterLink: { props: ["to"], template: "<a :href=\"to\"><slot /></a>" } },
  },
};

afterEach(() => vi.unstubAllGlobals());

describe("the rating version view", () => {
  it("shows the slug, version, status and the pinned model", async () => {
    getRatingVersion.mockResolvedValue(RATING);
    render(RatingVersionView, { props, ...mounted });

    expect(await screen.findByText(/fremtpl2-demo/)).toBeInTheDocument();
    expect(screen.getByText("approved")).toBeInTheDocument();
    expect(screen.getByText(/model:fremtpl2-glm-7edfde@1/)).toBeInTheDocument();
    expect(screen.getByText(RATING.dataset_version_id)).toBeInTheDocument();
  });

  it("FR-25: links to the designer by the rating version's own slug and version", async () => {
    getRatingVersion.mockResolvedValue(RATING);
    render(RatingVersionView, { props, ...mounted });

    const link = await screen.findByRole("link", { name: "Open in the designer" });
    expect(link).toHaveAttribute("href", "/rating/fremtpl2-demo/v/1/design");
  });

  it("FR-25: links one rate table editor per pinned table, with no list call (RL-1475 item 3)", async () => {
    getRatingVersion.mockClear();
    getRatingVersion.mockResolvedValue({
      ...RATING,
      pins: { rate_tables: ["rate_table:area@3", "rate_table:band@2"] },
    });
    render(RatingVersionView, { props, ...mounted });

    const area = await screen.findByRole("link", { name: "area@3" });
    expect(area).toHaveAttribute("href", "/rating/fremtpl2-demo/v/1/tables/area");
    expect(screen.getByRole("link", { name: "band@2" })).toHaveAttribute(
      "href",
      "/rating/fremtpl2-demo/v/1/tables/band",
    );
    expect(getRatingVersion).toHaveBeenCalledTimes(1); // the one read; the pins come with it
  });

  it("shows no table links when the rating version pins no rate table", async () => {
    getRatingVersion.mockResolvedValue(RATING);
    render(RatingVersionView, { props, ...mounted });

    await screen.findByText(/fremtpl2-demo/);
    expect(screen.queryByText("Rate tables")).not.toBeInTheDocument();
  });

  it("shows the loading state while the read is in flight", () => {
    // A never-resolving promise keeps `loading` true, so the view renders the loading
    // placeholder rather than the rating or an error.
    getRatingVersion.mockReturnValue(new Promise(() => {}));
    render(RatingVersionView, { props, ...mounted });

    expect(screen.getByText("Loading…")).toBeInTheDocument();
  });

  it("renders a 404 from its title and detail", async () => {
    // The by-id read route answers 404 for a rating version that does not exist; the view
    // must surface the problem, not a blank page.
    const { ProblemError } = await import("@/api/problem");
    getRatingVersion.mockRejectedValue(new ProblemError({
      type: "https://docs.gi-pricing.dev/errors/not-found",
      title: "Not found",
      status: 404,
      code: "NOT_FOUND",
      detail: "No rating version 01a04394-338b-7651-9e42-c73ee70396f8.",
      errors: [],
      trace_id: "abc123",
    }));
    render(RatingVersionView, { props, ...mounted });

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Not found");
    expect(alert).toHaveTextContent("No rating version");
  });
});
