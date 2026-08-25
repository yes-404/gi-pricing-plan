import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import PartitionTable from "../PartitionTable.vue";

describe("PartitionTable", () => {
  it("puts one column per partition beside the metric name", () => {
    render(PartitionTable, {
      props: {
        title: "Residual summary",
        columns: ["Train", "Holdout"],
        rows: [{ name: "Mean", values: [0.0004, -0.0011] }],
      },
    });
    const table = screen.getByRole("table", { name: /residual summary/i });
    expect(within(table).getAllByRole("columnheader").map((h) => h.textContent?.trim())).toEqual([
      "Metric",
      "Train",
      "Holdout",
    ]);
    expect(within(table).getByRole("rowheader", { name: "Mean" })).toBeInTheDocument();
  });

  it("writes an absent value as an em dash", () => {
    render(PartitionTable, {
      props: {
        title: "Residual summary",
        columns: ["Train"],
        rows: [{ name: "Mean", values: [null] }],
      },
    });
    const row = screen.getByRole("row", { name: /mean/i });
    expect(within(row).getAllByRole("cell")[0]).toHaveTextContent("—");
  });
});
