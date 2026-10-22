// RL-1835 (ii) 2 and (iii) 1, 4: the view hands the Rating Version's sub-graph pins to the designer
// and never writes to a Rating Version (no route edits an existing version's pins).
import userEvent from "@testing-library/user-event";
import { render, screen } from "@testing-library/vue";
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from "vitest";

import { FEES, FRAGMENT, REFUND, withMounts } from "@/components/dag/__tests__/mountFixtures";

import RatingDesignView from "../RatingDesignView.vue";

const api = vi.hoisted(() => ({
  getRatingVersionByRef: vi.fn(),
  getRatingAlgorithm: vi.fn(),
  saveRatingAlgorithm: vi.fn(),
  request: vi.fn(),
}));

vi.mock("@/api/ratingVersions", () => ({ getRatingVersionByRef: api.getRatingVersionByRef }));
vi.mock("@/api/ratingAlgorithms", () => ({
  getRatingAlgorithm: api.getRatingAlgorithm,
  saveRatingAlgorithm: api.saveRatingAlgorithm,
  validateRatingAlgorithm: () => Promise.resolve({ issues: [] }),
}));
// Every request that would leave the browser passes here, whichever api module makes it.
vi.mock("@/api/client", () => ({ request: api.request }));

beforeAll(() => {
  globalThis.ResizeObserver ??= class {
    observe(): void {}
    unobserve(): void {}
    disconnect(): void {}
  };
});

const RATING = {
  id: "01a04394-338b-7651-9e42-c73ee70396f8",
  slug: "fremtpl2-demo",
  version: 1,
  algorithm_ref: "rating_algorithm:motor-gb@1",
  model_reference_mode: "exact",
  pins: { rate_tables: [], sub_graphs: [FEES.ref, REFUND.ref] },
};
const props = { slug: "fremtpl2-demo", version: "1" };
const mounted = { global: { stubs: { RouterLink: { template: "<a><slot /></a>" } } } };

beforeEach(() => {
  api.getRatingVersionByRef.mockResolvedValue(RATING);
  api.getRatingAlgorithm.mockResolvedValue(structuredClone(withMounts));
  api.saveRatingAlgorithm.mockResolvedValue({ id: RATING.id, slug: "motor-gb", version: 2 });
  api.request.mockResolvedValue(FRAGMENT);
});
afterEach(() => vi.clearAllMocks());

describe("the rating design view with sub-graph mounts", () => {
  it("draws the loaded mounts and saves them, without any write to a Rating Version", async () => {
    render(RatingDesignView, { props, ...mounted });
    await screen.findByLabelText(/sub-graph mount m_fees/);
    await userEvent.click(screen.getByRole("button", { name: "Save as new version" }));
    await screen.findByText("Saved as motor-gb@2");
    const [body] = api.saveRatingAlgorithm.mock.calls[0] as [{ sub_graphs: { mount_point: string }[] }];
    expect(body.sub_graphs.map((m) => m.mount_point)).toEqual(["m_fees", "m_refund"]);
    for (const [path, init] of api.request.mock.calls as [string, { method?: string } | undefined][]) {
      const write = init?.method !== undefined && init.method !== "GET";
      expect(write && path.startsWith("/rating-versions")).toBe(false);
    }
  });

  it("enables adding a mount when the Rating Version pins sub-graphs", async () => {
    render(RatingDesignView, { props, ...mounted });
    await screen.findByLabelText(/sub-graph mount m_fees/);
    expect(screen.getByRole("button", { name: "Add sub-graph mount" })).toBeEnabled();
  });

  it("disables adding a mount, with the reason, when it pins none", async () => {
    api.getRatingVersionByRef.mockResolvedValue({ ...RATING, pins: { rate_tables: [] } });
    render(RatingDesignView, { props, ...mounted });
    await screen.findByLabelText(/sub-graph mount m_fees/);
    expect(screen.getByRole("button", { name: "Add sub-graph mount" })).toBeDisabled();
    expect(screen.getByText("This Rating Version pins no sub-graph")).toBeInTheDocument();
  });
});
