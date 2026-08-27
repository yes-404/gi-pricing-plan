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
  global: { stubs: { RouterLink: { template: "<a><slot /></a>" } } },
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
