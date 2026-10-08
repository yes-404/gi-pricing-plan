import userEvent from "@testing-library/user-event";
import { render, screen } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import type { RatingStep } from "@/api/ratingAlgorithms";

import { stepProblems } from "../problems";
import StepInspector from "../StepInspector.vue";
import { valid } from "./fixtures";

const byId = (id: string): RatingStep => {
  const step = valid.steps.find((s) => s.step_id === id);
  if (step === undefined) throw new Error(id);
  return step;
};

const base = {
  isNew: false,
  inputContract: valid.input_contract,
  rateTablePins: ["rate_table:motor-expense@3", "rate_table:motor-base@1"],
  versionMode: "exact" as const,
};

function lastStep(emitted: Record<string, unknown[][]>): Record<string, unknown> {
  const all = emitted["update:step"] ?? [];
  return all[all.length - 1]?.[0] as Record<string, unknown>;
}

describe("the step inspector, one section per step type", () => {
  it("FR-213: an input step edits its input-contract entry, and a bound is sent as the typed string", async () => {
    const { emitted } = render(StepInspector, { props: { ...base, step: byId("s_in_age") } });
    const min = screen.getByLabelText("Minimum");
    await userEvent.clear(min);
    await userEvent.type(min, "18.5");
    const all = (emitted() as Record<string, unknown[][]>)["update:inputContract"] ?? [];
    const contract = all.at(-1)?.[0] as Array<Record<string, unknown>>;
    const entry = contract.find((f) => f["name"] === "driver_age");
    expect(entry?.["min"]).toBe("18.5");
    expect(typeof entry?.["min"]).toBe("string");
    expect(screen.getByLabelText("Input type")).toHaveValue("int");
  });

  it("FR-215: an existing step_id is read-only and a label edit keeps it", async () => {
    const { emitted } = render(StepInspector, { props: { ...base, step: byId("s_area") } });
    expect(screen.getByLabelText("Step id")).toHaveAttribute("readonly");
    const label = screen.getByLabelText("Label");
    await userEvent.type(label, "!");
    expect(lastStep(emitted() as Record<string, unknown[][]>)["step_id"]).toBe("s_area");
    expect(lastStep(emitted() as Record<string, unknown[][]>)["label"]).toBe("Area!");
  });

  it("FR-220: a table step chooses its rate table from the version's pins only", () => {
    render(StepInspector, { props: { ...base, step: byId("s_expense") } });
    const select = screen.getByLabelText("Rate table");
    expect(select.tagName).toBe("SELECT");
    const options = Array.from(select.querySelectorAll("option")).map((o) => o.value);
    expect(options).toEqual(["rate_table:motor-expense@3", "rate_table:motor-base@1"]);
    expect(screen.queryByRole("textbox", { name: "Rate table" })).toBeNull();
    expect(screen.getByLabelText("Key expressions")).toBeInTheDocument();
  });

  it("FR-221: a lookup step's as_at is a required, explicit field over effective_date and the declared date inputs", () => {
    const lookup = byId("s_area");
    const withExtra = [
      ...base.inputContract,
      { name: "inception_date", type: "date" as const },
      { name: "driver_age_band", type: "string" as const },
    ];
    render(StepInspector, {
      props: { ...base, inputContract: withExtra, step: lookup },
    });
    const select = screen.getByLabelText("As at (date input)");
    expect(select).toHaveValue("effective_date");
    const options = Array.from(select.querySelectorAll("option"))
      .map((o) => o.value)
      .filter((v) => v !== "");
    // effective_date once (it is declared too), the other declared date input, no string input, no "now".
    expect(options).toEqual(["effective_date", "inception_date"]);
    expect(stepProblems({ ...lookup, as_at: "" } as RatingStep)).toContain(
      "as_at is required (FR-221)",
    );
  });

  it("FR-221: a new lookup offers effective_date even when the algorithm does not declare it as an input", () => {
    render(StepInspector, {
      props: {
        ...base,
        inputContract: base.inputContract.filter((f) => f.name !== "effective_date"),
        step: { ...byId("s_area"), as_at: "" } as RatingStep,
      },
    });
    const options = Array.from(screen.getByLabelText("As at (date input)").querySelectorAll("option"))
      .map((o) => o.value)
      .filter((v) => v !== "");
    expect(options).toEqual(["effective_date"]);
  });

  it("FR-222 and FR-223: a model_call shows the version's mode read-only and flags a step that differs", () => {
    const call = byId("s_rp");
    const { unmount } = render(StepInspector, { props: { ...base, step: call } });
    expect(
      screen.getByText(/Model reference mode: exact \(set on the Rating Version, FR-223\)/),
    ).toBeInTheDocument();
    expect(screen.queryByRole("combobox", { name: /mode/i })).toBeNull();
    expect(screen.queryByRole("status")).toBeNull();
    unmount();

    render(StepInspector, {
      props: { ...base, step: { ...call, mode: "approximation" } as RatingStep },
    });
    const flag = screen.getByRole("status");
    expect(flag).toHaveTextContent(/approximation/);
    expect(flag).toHaveTextContent(/exact/);
  });

  it("FR-223: a new model_call step takes the version's mode", async () => {
    const fresh = {
      step_id: "s_new",
      type: "model_call",
      label: "New",
      mode: "approximation",
    } as RatingStep;
    const { emitted } = render(StepInspector, {
      props: { ...base, isNew: true, step: fresh },
    });
    await userEvent.type(screen.getByLabelText("Label"), "x");
    expect(lastStep(emitted() as Record<string, unknown[][]>)["mode"]).toBe("exact");
  });

  it("FR-225: an empty reason_code on a constraint step is a blocking problem", async () => {
    const constraint = { ...byId("s_minprem"), reason_code: "" } as RatingStep;
    render(StepInspector, { props: { ...base, step: constraint } });
    expect(screen.getByText("reason_code is required (FR-225)")).toBeInTheDocument();
    expect(stepProblems(constraint)).toEqual(["reason_code is required (FR-225)"]);
    expect(stepProblems(byId("s_minprem"))).toEqual([]);
  });

  it("FR-226: an output step requires its rounding mode and dp", () => {
    const out = byId("s_out");
    render(StepInspector, { props: { ...base, step: out } });
    const mode = screen.getByLabelText("Rounding mode");
    expect(Array.from(mode.querySelectorAll("option")).map((o) => o.value)).toEqual([
      "half_even",
      "half_up",
      "ceiling",
      "floor",
    ]);
    expect(screen.getByLabelText("Decimal places (dp)")).toHaveValue(0);
    const broken = { ...out, rounding: { mode: "", dp: Number.NaN } } as unknown as RatingStep;
    expect(stepProblems(broken)).toEqual([
      "rounding mode is required (FR-226)",
      "rounding dp is required (FR-226)",
    ]);
  });

  it("FR-244: an expression step edits expr as text, with no function picker", async () => {
    const { emitted } = render(StepInspector, { props: { ...base, step: byId("s_office") } });
    const expr = screen.getByLabelText("Expression");
    expect(expr.tagName).toBe("TEXTAREA");
    expect(screen.queryByRole("combobox", { name: /function/i })).toBeNull();
    await userEvent.type(expr, "+1");
    expect(lastStep(emitted() as Record<string, unknown[][]>)["expr"]).toBe(
      "risk_premium_minor * expense_factor+1",
    );
  });

  it("3.3.1: a field with a required-field problem is marked invalid and points at the problem list", () => {
    const constraint = { ...byId("s_minprem"), reason_code: "" } as RatingStep;
    render(StepInspector, { props: { ...base, step: constraint } });
    const field = screen.getByLabelText("Reason code");
    expect(field).toHaveAttribute("aria-invalid", "true");
    expect(field).toHaveAttribute("aria-describedby", "si-problems");
    expect(screen.getByLabelText("Condition")).not.toHaveAttribute("aria-invalid");
  });
});
