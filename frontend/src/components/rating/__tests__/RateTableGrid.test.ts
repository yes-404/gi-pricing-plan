import userEvent from "@testing-library/user-event";
import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import type { RateTable } from "@/api/rateTables";

import RateTableGrid from "../RateTableGrid.vue";

const AREA_BY_BAND: RateTable = {
  slug: "area-by-band",
  version: 3,
  rateable: true,
  storage: "rows",
  keys: [
    { name: "area", type: "string" },
    { name: "band", type: "string" },
  ],
  value: { name: "relativity", type: "relativity", unit: "factor" },
};

const ROWS = [
  { area: "A", band: "17-20", relativity: "1.9200" },
  { area: "A", band: "21-24", relativity: "1.4100" },
];

describe("RateTableGrid (FR-228)", () => {
  it("orders the columns as declared, the value last, with its unit in the header", () => {
    render(RateTableGrid, { props: { table: AREA_BY_BAND, rows: [], edits: {}, errors: {} } });
    expect(screen.getAllByRole("columnheader").map((h) => h.textContent?.trim())).toEqual([
      "area",
      "band",
      "relativity (factor)",
    ]);
  });

  it("shows a value column that is money in minor units with its unit", () => {
    const money: RateTable = {
      ...AREA_BY_BAND,
      value: { name: "premium", type: "money_minor", unit: "pence" },
    };
    render(RateTableGrid, { props: { table: money, rows: [], edits: {}, errors: {} } });
    expect(screen.getAllByRole("columnheader").at(-1)?.textContent?.trim()).toBe("premium (pence)");
  });

  it("renders the key values as row headers and the stored value, or the edit over it", () => {
    render(RateTableGrid, {
      props: {
        table: AREA_BY_BAND,
        rows: ROWS,
        edits: { "A\u001f21-24": "1.5000" },
        errors: {},
      },
    });
    const rows = screen.getAllByRole("row").slice(1);
    expect(rows).toHaveLength(2);
    expect(within(rows[0]!).getAllByRole("rowheader").map((h) => h.textContent)).toEqual(["A", "17-20"]);
    expect(within(rows[0]!).getByRole("textbox")).toHaveValue("1.9200");
    expect(within(rows[1]!).getByRole("textbox")).toHaveValue("1.5000");
  });

  it("emits the row's key and the exact string typed", async () => {
    const { emitted } = render(RateTableGrid, {
      props: { table: AREA_BY_BAND, rows: ROWS, edits: {}, errors: {} },
    });
    const input = screen.getAllByRole("textbox")[0]!;
    await userEvent.clear(input);
    await userEvent.type(input, "2.000000000000000001");
    expect((emitted().edit as unknown[][]).at(-1)).toEqual(["A\u001f17-20", "2.000000000000000001"]);
  });

  it("marks the cell a server error names", () => {
    render(RateTableGrid, {
      props: {
        table: AREA_BY_BAND,
        rows: ROWS,
        edits: {},
        errors: { "A\u001f17-20": "no such key" },
      },
    });
    const [first, second] = screen.getAllByRole("textbox");
    expect(first).toHaveAttribute("aria-invalid", "true");
    expect(second).toHaveAttribute("aria-invalid", "false");
  });
});
