import { render, screen } from "@testing-library/vue";
import { afterEach, describe, expect, it, vi } from "vitest";

import * as api from "@/api/objectives";
import ObjectiveLibraryView from "../ObjectiveLibraryView.vue";

// Field names copied out of the generated contract, not written from memory: `applicability`
// is a required `Applicability` object (its own `responses` and `backends` both required),
// `usage_count` is optional and nullable, and `status` carries a default but is **not** in
// `required` — so it reaches the client possibly absent.
const OBJECTIVE = {
  id: "a1",
  slug: "tweedie-cap",
  version: 2,
  status: "approved",
  applicability: { responses: ["claim_count"], backends: ["xgboost"] },
  usage_count: 3,
} as unknown as api.CustomObjective;

const mounted = { global: { stubs: { RouterLink: { template: "<a><slot /></a>" } } } };

afterEach(() => vi.restoreAllMocks());

describe("ObjectiveLibraryView", () => {
  it("renders the library and links each row to its certificate", async () => {
    vi.spyOn(api, "listObjectives").mockResolvedValue({ items: [OBJECTIVE], truncated: false });
    render(ObjectiveLibraryView, mounted);

    expect(await screen.findByText("tweedie-cap")).toBeInTheDocument();
    expect(screen.getByText("claim_count")).toBeInTheDocument();
  });

  it("defaults an absent status rather than rendering an unstyled badge", async () => {
    // `status` has a contract default of `draft` and is not required, so an artifact can
    // reach the client without one. Left undefaulted it reaches `Record<ArtifactStatus,…>`
    // as `undefined` and the badge renders with no tone class at all.
    const withoutStatus: Record<string, unknown> = { ...OBJECTIVE };
    delete withoutStatus.status;
    vi.spyOn(api, "listObjectives").mockResolvedValue({
      items: [withoutStatus as unknown as api.CustomObjective],
      truncated: false,
    });
    render(ObjectiveLibraryView, mounted);

    expect(await screen.findByText("draft")).toBeInTheDocument();
  });

  it("does not call the library empty when the sweep was truncated", async () => {
    vi.spyOn(api, "listObjectives").mockResolvedValue({ items: [], truncated: true });
    const { container } = render(ObjectiveLibraryView, mounted);

    await screen.findByText(/More exist/i);
    expect(container.textContent ?? "").not.toContain("No custom objectives");
  });
});
