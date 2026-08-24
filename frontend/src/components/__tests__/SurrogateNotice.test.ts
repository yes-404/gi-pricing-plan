import { render, screen } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import SurrogateNotice from "../SurrogateNotice.vue";

const SOURCE = "55555555-5555-4555-8555-555555555555";

describe("SurrogateNotice", () => {
  it("renders nothing for a model that approximates nothing", () => {
    const { container } = render(SurrogateNotice, { props: { approximatesModelId: null } });
    expect(container.textContent?.trim()).toBe("");
  });

  it("names the model whose predictions are the denominator", () => {
    render(SurrogateNotice, { props: { approximatesModelId: SOURCE } });
    expect(screen.getByText(SOURCE)).toBeInTheDocument();
  });

  it("says the comparison is against predictions and not against observed claims", () => {
    render(SurrogateNotice, { props: { approximatesModelId: SOURCE } });
    expect(screen.getByRole("note")).toHaveTextContent(/not against observed claims/i);
  });
});
