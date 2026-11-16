import { render, screen } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import UnseenLevelRows from "../UnseenLevelRows.vue";

const NOTE = "A quote with such a level is refused, unless the factor declares “map to base”.";

function show(notes: { label: string; rows: number | null; exposure: string | null }[]) {
  return render(UnseenLevelRows, { props: { notes, note: NOTE } });
}

describe("UnseenLevelRows", () => {
  it("states a count with its exposure", () => {
    show([{ label: "Holdout", rows: 50, exposure: "50.0" }]);

    expect(screen.getByLabelText("Rows on a level this fit never saw")).toHaveTextContent(
      "Holdout: 50 rows (exposure 50.0) are left out of every figure on this page.",
    );
  });

  it("says none left out for 0, and not recorded for null, never one for the other", () => {
    show([
      { label: "Train", rows: 0, exposure: "0" },
      { label: "Holdout", rows: null, exposure: null },
    ]);
    const section = screen.getByLabelText("Rows on a level this fit never saw");

    expect(section).toHaveTextContent("Train: none left out.");
    expect(section).toHaveTextContent("Holdout: not recorded.");
    expect(section).not.toHaveTextContent("Holdout: none left out");
  });

  it("carries the caller's sentence about a quote", () => {
    show([{ label: "Holdout", rows: 0, exposure: "0" }]);

    expect(screen.getByLabelText("Rows on a level this fit never saw")).toHaveTextContent(NOTE);
  });
});
