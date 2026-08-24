import { render, screen } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import ModelRefLink from "@/components/ModelRefLink.vue";

// The component renders a RouterLink, which needs the router symbol. A stub keeps this test
// about the parse rather than about routing; ModelComparisonView.test.ts exercises the real
// router.
const global = {
  stubs: { RouterLink: { props: ["to"], template: "<a :href='to'><slot /></a>" } },
};

describe("ModelRefLink", () => {
  it("links a parseable ref to the model detail route, at its version", () => {
    render(ModelRefLink, { props: { modelRef: "model:motor-ad-frequency@7" }, global });
    const link = screen.getByRole("link", { name: /motor-ad-frequency/ });
    expect(link).toHaveAttribute("href", "/models/motor-ad-frequency?version=7");
    // The version is visible, not only in the href: `02` §4.11 keeps refs so "a comparison
    // read years later still names exactly which model versions it held".
    expect(link).toHaveTextContent("motor-ad-frequency@7");
  });

  // `comparison.py` imports Weighting, SplitRef and DecimalStr and never imports `refs`, so
  // `model_ref` is an unconstrained string on a perfectly valid artifact. An unparseable ref
  // is shown, not dropped — dropping it would leave a metric row with a nameless column.
  it("renders an unparseable ref as plain text, with no link", () => {
    render(ModelRefLink, { props: { modelRef: "legacy-model-4" }, global });
    expect(screen.getByText("legacy-model-4")).toBeInTheDocument();
    expect(screen.queryByRole("link")).toBeNull();
  });
});
