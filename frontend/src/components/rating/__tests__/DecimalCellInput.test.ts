import userEvent from "@testing-library/user-event";
import { render, screen } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import DecimalCellInput from "../DecimalCellInput.vue";

describe("DecimalCellInput (FR-10, FR-21)", () => {
  it("emits exactly the string typed, past the precision of a float", async () => {
    const { emitted } = render(DecimalCellInput, { props: { modelValue: "1.10" } });
    const input = screen.getByRole("textbox");
    await userEvent.clear(input);
    await userEvent.type(input, "1.100000000000000001");
    expect((emitted()["update:modelValue"] as string[][]).at(-1)).toEqual(["1.100000000000000001"]);
  });

  it("flags a non-decimal entry before anything is sent", async () => {
    render(DecimalCellInput, { props: { modelValue: "" } });
    await userEvent.type(screen.getByRole("textbox"), "1.2.3");
    expect(screen.getByRole("textbox")).toHaveAttribute("aria-invalid", "true");
  });

  it("accepts a plain decimal, a negative one and an empty field as syntax", async () => {
    render(DecimalCellInput, { props: { modelValue: "" } });
    const input = screen.getByRole("textbox");
    await userEvent.type(input, "-0.25");
    expect(input).toHaveAttribute("aria-invalid", "false");
  });

  it("takes whole numbers only for an integer column (money in minor units, a count)", async () => {
    render(DecimalCellInput, { props: { modelValue: "", integer: true } });
    const input = screen.getByRole("textbox");
    await userEvent.type(input, "12.5");
    expect(input).toHaveAttribute("aria-invalid", "true");
  });

  it("shows the server's error on the cell and ties it to the input", () => {
    render(DecimalCellInput, { props: { modelValue: "-1", invalid: "below the minimum" } });
    const input = screen.getByRole("textbox");
    expect(input).toHaveAttribute("aria-invalid", "true");
    expect(input).toHaveAccessibleDescription("below the minimum");
  });
});

// NFR-463 / WCAG 3.3.1 (FD-1959 F1): a syntax error is said in words and tied to the input, not
// only coloured and flagged with aria-invalid.
describe("DecimalCellInput: a syntax error is described (NFR-463, FD-1959 F1)", () => {
  it("describes a malformed decimal in words, visibly and to assistive technology", async () => {
    render(DecimalCellInput, { props: { modelValue: "" } });
    const input = screen.getByRole("textbox");
    await userEvent.type(input, "1.2.3");
    expect(input).toHaveAttribute("aria-invalid", "true");
    expect(input).toHaveAccessibleDescription("Enter a decimal number");
    expect(screen.getByText("Enter a decimal number")).toBeVisible();
  });

  it("describes a non-integer in an integer column as a whole-number error", async () => {
    render(DecimalCellInput, { props: { modelValue: "", integer: true } });
    const input = screen.getByRole("textbox");
    await userEvent.type(input, "12.5");
    expect(input).toHaveAccessibleDescription("Enter a whole number");
    expect(screen.getByText("Enter a whole number")).toBeVisible();
  });
});
