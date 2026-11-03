import userEvent from "@testing-library/user-event";
import { render, screen } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import QuoteForm from "../QuoteForm.vue";
import type { ContractField } from "../quoteForm";

const FIELDS: ContractField[] = [
  { name: "channel", type: "enum", nullable: false, domain: ["direct", "broker"] },
  { name: "driver_age", type: "int", nullable: false, min: 17, max: 99 },
];

// NFR-463 / WCAG 3.3.1 (FD-1974 L-7): the enum control must carry the same invalid-state pair
// as the text controls, or its "Required" message is shown but never tied to it.
describe("QuoteForm: a refused enum is tied to its problem text (FD-1974 L-7)", () => {
  it("marks a required enum left unchosen invalid and describes it by its problem", async () => {
    render(QuoteForm, { props: { fields: FIELDS } });
    await userEvent.click(screen.getByRole("button", { name: "Score quote" }));

    const select = screen.getByLabelText("channel");
    expect(select).toHaveAttribute("aria-invalid", "true");
    expect(select).toHaveAccessibleDescription(/Required/);
  });

  it("leaves a chosen enum unmarked", async () => {
    render(QuoteForm, { props: { fields: FIELDS } });
    await userEvent.selectOptions(screen.getByLabelText("channel"), "direct");
    await userEvent.click(screen.getByRole("button", { name: "Score quote" }));

    expect(screen.getByLabelText("channel")).not.toHaveAttribute("aria-invalid");
  });
});

// FD-1974 L-1 on this caller: a field's hint (here the int range) is the control's description
// as well as its problem; the problem is joined to the hint, not replacing it.
describe("QuoteForm: a hint and a problem both describe the control (FD-1974 L-1)", () => {
  it("describes a ranged int by its hint, and by hint plus problem once refused", async () => {
    render(QuoteForm, { props: { fields: FIELDS } });
    const age = screen.getByLabelText("driver_age");
    expect(age).toHaveAccessibleDescription(/17/);

    await userEvent.click(screen.getByRole("button", { name: "Score quote" }));
    expect(age).toHaveAccessibleDescription(/17.*Required|Required.*17/s);
  });
});
