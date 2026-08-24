import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import { DIAGNOSTICS } from "@/views/__tests__/fixtures";

import ComplexityTable from "../ComplexityTable.vue";

describe("ComplexityTable", () => {
  it("shows each ratio beside the threshold in force", () => {
    render(ComplexityTable, { props: { complexity: DIAGNOSTICS.complexity } });
    const row = screen.getByRole("row", { name: /exposure per parameter/i });
    const cells = within(row).getAllByRole("cell");
    expect(cells[0]).toHaveTextContent("1903.4");
    expect(cells[1]).toHaveTextContent("1000");
  });

  it("says no threshold is in force rather than leaving the cell blank", () => {
    render(ComplexityTable, { props: { complexity: DIAGNOSTICS.complexity } });
    const row = screen.getByRole("row", { name: /factor count/i });
    expect(within(row).getAllByRole("cell")[1]).toHaveTextContent(/none set/i);
  });

  it("does not call an unset threshold a pass", () => {
    render(ComplexityTable, { props: { complexity: DIAGNOSTICS.complexity } });
    const row = screen.getByRole("row", { name: /factor count/i });
    expect(within(row).getAllByRole("cell")[2]).toHaveTextContent("—");
  });

  it("marks a ratio under its floor as a breach of the threshold in force", () => {
    render(ComplexityTable, {
      props: {
        complexity: { ...DIAGNOSTICS.complexity, exposure_per_parameter: 400 },
      },
    });
    const row = screen.getByRole("row", { name: /exposure per parameter/i });
    expect(within(row).getAllByRole("cell")[2]).toHaveTextContent(/below/i);
  });
});
