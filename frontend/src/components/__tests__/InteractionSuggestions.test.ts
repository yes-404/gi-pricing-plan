import { render, screen } from "@testing-library/vue";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import type { ShapInteraction, ShapSummary } from "@/api/models";
import { cellUnder } from "@/test-tables";

import InteractionSuggestions from "../InteractionSuggestions.vue";

function pair(
  a: string,
  b: string,
  strength: number,
  ratio: number | null,
): ShapInteraction {
  return { pair: [a, b], strength, holdout_strength_ratio: ratio } as ShapInteraction;
}

function summary(interactions: ShapInteraction[]): ShapSummary {
  return { top_interactions: interactions } as ShapSummary;
}

function panel(
  interactions: ShapInteraction[] | null,
  interactionsAvailable = true,
) {
  return render(InteractionSuggestions, {
    props: {
      summary: interactions === null ? null : summary(interactions),
      interactionsAvailable,
    },
  });
}

function table(): HTMLElement {
  return screen.getByRole("table", { name: /ranked by SHAP interaction strength/i });
}

describe("the interaction suggestion panel", () => {
  it("shows each pair with its strength and its holdout ratio", () => {
    panel([pair("driv_age", "area", 0.0412, 0.83)]);
    const t = table();

    expect(cellUnder(t, /driv_age/, "Pair")).toHaveTextContent("driv_age × area");
    expect(cellUnder(t, /driv_age/, "Strength")).toHaveTextContent("0.0412");
    expect(cellUnder(t, /driv_age/, "Holdout ratio")).toHaveTextContent("0.83");
  });

  it("keeps the artifact's order and does not re-rank by ratio", () => {
    // The ratio is evidence beside a candidate, not a competing score. Sorting by it would
    // make it the admission test FR-MODEL-128 forbids — the ranking is by strength, which
    // is the order the artifact stores.
    panel([
      pair("strong", "pair", 0.9, 0.20),
      pair("weaker", "pair", 0.1, 0.99),
    ]);

    const rows = Array.from(table().querySelectorAll("tbody tr"))
      .map((r) => r.textContent ?? "");
    expect(rows[0]).toContain("strong");
    expect(rows[1]).toContain("weaker");
  });

  it("implies no threshold — no cutoff, no verdict, no recommendation", () => {
    // FR-MODEL-128: ranked evidence, never an admission test. A "recommended" marker or a
    // pass/fail colour would be a threshold wearing a different hat, and would undo
    // FR-MODEL-79's refusal to write a Factor by having the UI effectively do it.
    panel([pair("a", "b", 0.9, 0.99), pair("c", "d", 0.1, 0.10)]);

    const text = document.body.textContent ?? "";
    expect(text).not.toMatch(/recommend|significant|passes|fails|threshold|strong enough/i);
    // And nothing compares a ratio to 1, which OQ-MODEL-38 shows is not the neutral point.
    expect(text).not.toMatch(/close to 1|near 1|above 1|below 1/i);
  });

  it("says an interaction is authored, never added", () => {
    // FR-MODEL-79: the platform never writes a Factor into a Model Spec.
    panel([pair("a", "b", 0.5, 0.9)]);

    expect(screen.getByText(/authored decision/i)).toBeInTheDocument();
    expect(screen.getByText(/intent and a rationale/i)).toBeInTheDocument();
  });

  it("emits the pair to author rather than creating anything itself", async () => {
    const user = userEvent.setup();
    const { emitted } = panel([pair("driv_age", "area", 0.5, 0.9)]);

    await user.click(screen.getByRole("button", { name: /Author a factor/ }));

    expect(emitted().author?.at(-1)).toEqual([["driv_age", "area"]]);
  });

  it("shows an absent ratio as absent, beside pairs that have one", () => {
    // A single `null` is a finding — that pair had zero in-sample strength — and can be
    // said plainly. It is only *all* of them being absent that is ambiguous.
    panel([pair("a", "b", 0.5, 0.9), pair("c", "d", 0.0, null)]);

    expect(cellUnder(table(), /c ×/, "Holdout ratio")).toHaveTextContent("—");
    expect(screen.queryByText(/not available for this artifact/i)).toBeNull();
  });

  it("words an all-absent set so it is true of both causes", async () => {
    // OQ-MODEL-39: a pre-W6b-5a artifact and a genuinely zero-strength one are
    // indistinguishable here. "No structure found" would be a claim about the data that
    // the panel cannot support.
    panel([pair("a", "b", 0.0, null), pair("c", "d", 0.0, null)]);

    expect(screen.getByText(/not available for this artifact/i)).toBeInTheDocument();
    expect(document.body.textContent).not.toMatch(/no structure (was )?found/i);
  });

  it("offers a rebuild without promising it yields a value", () => {
    // A genuine all-zero artifact recomputes to all-null, so a promise would be false.
    panel([pair("a", "b", 0.0, null)]);

    expect(screen.getByText(/will still show none/i)).toBeInTheDocument();
  });

  it("distinguishes a backend that cannot find interactions from finding none", () => {
    // `interactions_available` is a capability, not an empty list: "no interactions found"
    // is a finding LightGBM cannot make.
    panel([], false);

    expect(screen.getByText(/capability of the backend rather than a finding/i))
      .toBeInTheDocument();
    expect(screen.queryByText(/No interaction candidates were found/)).toBeNull();
  });

  it("says none were found only when the backend could have found some", () => {
    panel([], true);

    expect(screen.getByText(/No interaction candidates were found/)).toBeInTheDocument();
  });

  it("says a model has no summary rather than implying it has no interactions", () => {
    panel(null, true);

    expect(screen.getByText(/no SHAP summary/i)).toBeInTheDocument();
  });
});
