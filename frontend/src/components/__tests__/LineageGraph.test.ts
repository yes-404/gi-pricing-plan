import { render, screen } from "@testing-library/vue";
import { describe, expect, it, vi } from "vitest";

import { cellUnder } from "@/test-tables";

import LineageGraph from "../LineageGraph.vue";

vi.mock("vue-echarts", () => ({
  default: { template: "<div data-testid=\"chart\" />", props: ["option"] },
}));

const LINEAGE = {
  version_id: "11111111-1111-4111-8111-111111111111",
  built_from: {
    parent_version_id: "22222222-2222-4222-8222-222222222222",
    operation: "sample",
    parameters: {},
  },
  depends_on_this: {
    derived_versions: [
      { version_id: "33333333-3333-4333-8333-333333333333", version: 3, operation: "split" },
    ],
    models: [
      { model_id: "44444444-4444-4444-8444-444444444444", slug: "motor-freq-2026", status: "approved" },
    ],
    rating_versions: [],
    monitoring_baselines: [],
  },
};

describe("the lineage graph", () => {
  it("renders a chart and a table that says what the chart says", () => {
    render(LineageGraph, { props: { lineage: LINEAGE, version: 2 } });
    expect(screen.getByTestId("chart")).toBeTruthy();
    const table = screen.getByRole("table", { name: "Lineage" });
    expect(table).toHaveTextContent("v2");
    expect(table).toHaveTextContent("v3");
    expect(table).toHaveTextContent("motor-freq-2026");
    expect(table).toHaveTextContent("approved");
    expect(table).toHaveTextContent("sample");
  });

  it("NFR-463: puts each lineage field under its own heading, read by label", () => {
    render(LineageGraph, { props: { lineage: LINEAGE, version: 2 } });
    const table = screen.getByRole("table", { name: "Lineage" });
    expect(cellUnder(table, /^Built from/, "Operation")).toHaveTextContent("sample");
    expect(cellUnder(table, /^Derived version/, "Name")).toHaveTextContent("v3");
    expect(cellUnder(table, /^Derived version/, "Operation")).toHaveTextContent("split");
    expect(cellUnder(table, /^Model/, "Name")).toHaveTextContent("motor-freq-2026");
    expect(cellUnder(table, /^Model/, "Status")).toHaveTextContent("approved");
    expect(cellUnder(table, /^Model/, "Operation")).toHaveTextContent("—");
  });

  it("renders a single node when nothing depends on the version", () => {
    render(LineageGraph, {
      props: {
        lineage: {
          version_id: "11111111-1111-4111-8111-111111111111",
          built_from: null,
          depends_on_this: {
            derived_versions: [],
            models: [],
            rating_versions: [],
            monitoring_baselines: [],
          },
        },
        version: 1,
      },
    });
    const table = screen.getByRole("table", { name: "Lineage" });
    expect(table).toHaveTextContent("v1");
    expect(table).not.toHaveTextContent("v3");
  });
});
