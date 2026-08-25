import { render, screen } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import type { SpecProblem, SpecProblemKind } from "@/api/modelSpecs";

import SpecProblemList from "../SpecProblemList.vue";

/**
 * All eleven, including `complexity_limit`.
 *
 * That one **cannot be produced by a default workspace**: `model_specs.py` resolves
 * `modelling.max_factor_count` and `modelling.min_exposure_per_parameter` to `None` unless
 * a workspace sets them, and records the decision — "an unset limit means 'no gate', not
 * 'gate at zero'" (OQ-MODEL-6). A suite built from cases a live backend would emit would
 * therefore cover ten of eleven and read as complete. This component renders a payload, so
 * every kind is constructible here regardless; the list is written out in full rather than
 * derived from anything, so a member added to the contract fails the count assertion below.
 */
const ALL: SpecProblemKind[] = [
  "dataset_not_validated",
  "factor_missing",
  "factor_prohibited",
  "factor_unresolvable",
  "split_missing",
  "split_invalid",
  "response_missing",
  "offset_missing",
  "model_offset_unresolvable",
  "complexity_limit",
  "objective_unsupported",
];

function problem(kind: SpecProblemKind, over: Partial<SpecProblem> = {}): SpecProblem {
  return { kind, message: `message for ${kind}`, subject: null, ...over };
}

function labels(problems: SpecProblem[]): string[] {
  const { container } = render(SpecProblemList, { props: { problems } });
  return Array.from(container.querySelectorAll("li")).map(
    (li) => li.querySelector("p")?.textContent?.trim() ?? "",
  );
}

describe("the spec problem list", () => {
  it("renders every one of the eleven kinds", () => {
    const rendered = labels(ALL.map((kind) => problem(kind)));

    expect(rendered).toHaveLength(ALL.length);
    expect(rendered.every((label) => label.length > 0)).toBe(true);
  });

  it("gives the eleven kinds mutually distinct labels", () => {
    // Not "every kind renders something" — a map giving two kinds the same label passes
    // that while leaving the analyst unable to tell them apart, which is the property
    // `SpecProblemKind`'s own docstring asserts: a closed set *because the frontend
    // renders each differently*.
    const rendered = labels(ALL.map((kind) => problem(kind)));

    expect(new Set(rendered).size).toBe(ALL.length);
  });

  it("renders all the problems, not the first", () => {
    // The specific failure `SpecValidation`'s docstring names: a builder surfacing one
    // error at a time "would make a ten-factor spec a ten-round conversation".
    const three = [
      problem("response_missing"),
      problem("split_missing"),
      problem("factor_prohibited"),
    ];

    expect(screen.queryAllByRole("listitem")).toHaveLength(0);
    expect(labels(three)).toHaveLength(3);
  });

  it("keeps the order the response gave them", () => {
    const forwards = labels([problem("split_missing"), problem("response_missing")]);
    const backwards = labels([problem("response_missing"), problem("split_missing")]);

    expect(forwards).toEqual([...backwards].reverse());
  });

  it("shows the backend's message rather than paraphrasing it", () => {
    // `SpecProblem` is "one reason a spec was refused, **in terms the caller can act
    // on**". The label is a heading over that message, never a substitute for it.
    render(SpecProblemList, {
      props: { problems: [problem("factor_missing", { message: "no factor named vehicle_age" })] },
    });

    expect(screen.getByText("no factor named vehicle_age")).toBeInTheDocument();
  });

  it("shows a subject when there is one, and nothing when there is not", () => {
    // `subject` is a workspace setting key in the complexity case, not a field name —
    // rendered as given, never routed to a form field.
    render(SpecProblemList, {
      props: {
        problems: [problem("complexity_limit", { subject: "modelling.max_factor_count" })],
      },
    });
    expect(screen.getByText("modelling.max_factor_count")).toBeInTheDocument();

    const { container } = render(SpecProblemList, {
      props: { problems: [problem("split_missing")] },
    });
    expect(container.querySelectorAll("li p")).toHaveLength(2);
  });

  it("renders nothing at all when there are no problems", () => {
    const { container } = render(SpecProblemList, { props: { problems: [] } });

    expect(container.querySelectorAll("li")).toHaveLength(0);
  });
});
