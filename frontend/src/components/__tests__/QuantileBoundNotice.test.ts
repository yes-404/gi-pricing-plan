import { render, screen } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import { boundOf, GBM_MODEL } from "@/views/__tests__/fixtures";

import QuantileBoundNotice from "../QuantileBoundNotice.vue";

// `stubs: { RouterLink: true }` discards the slot, so a link assertion would pass against an
// empty anchor. The template form keeps the slot and is what this repository uses everywhere.
const stubs = { global: { stubs: { RouterLink: { template: "<a><slot /></a>" } } } };

const BOUND_MODEL = boundOf(0.05);

describe("the quantile-bound notice", () => {
  it("says which side of the interval this model is, and links to the model it bounds", () => {
    render(QuantileBoundNotice, { props: { model: BOUND_MODEL }, ...stubs });
    expect(screen.getByText(/lower bound/i)).toBeInTheDocument();
    expect(screen.getByText(/motor-ad-frequency/)).toBeInTheDocument();
    expect(screen.getByText(/0\.05/)).toBeInTheDocument();
  });

  it("says a bound estimates a quantile and not a mean", () => {
    // FR-199. A page that shows a bound's numbers without this sentence is a page whose
    // reader takes them for the family's central estimate.
    render(QuantileBoundNotice, { props: { model: BOUND_MODEL }, ...stubs });
    expect(screen.getByText(/quantile, not the mean/i)).toBeInTheDocument();
  });

  it("calls the high side an upper bound", () => {
    // The side is read off alpha, and a bound fitted at 0.95 rendered as "lower" would be
    // the one error on this notice that reverses its meaning without looking wrong.
    render(QuantileBoundNotice, { props: { model: boundOf(0.95) }, ...stubs });
    expect(screen.getByText(/upper bound/i)).toBeInTheDocument();
  });

  it("renders nothing for a model that is not a bound", () => {
    const { container } = render(QuantileBoundNotice, { props: { model: GBM_MODEL }, ...stubs });
    expect(container.textContent?.trim()).toBe("");
  });
});
