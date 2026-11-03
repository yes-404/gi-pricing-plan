import { render, screen } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import FormField from "../FormField.vue";

function field(
  props: { fieldId: string; label: string; help?: string },
  control = '<input id="response" />',
) {
  return render(FormField, { props, slots: { default: control } });
}

describe("a labelled form field", () => {
  it("binds the label to the control, so the label finds it by name", () => {
    // The assertion is `getByLabelText`, not "a label element exists": it resolves the
    // association the same way a screen reader does, so a `for` pointing at nothing fails
    // here rather than passing as markup that looks right.
    field({ fieldId: "response", label: "Response" });

    expect(screen.getByLabelText("Response")).toBe(screen.getByRole("textbox"));
  });

  it("does not claim a control that is not the one it labels", () => {
    // The control against a `for` that matches nothing — which renders identically and is
    // the failure the test above exists to catch.
    field({ fieldId: "response", label: "Response" }, '<input id="something-else" />');

    expect(screen.queryByLabelText("Response")).toBeNull();
  });

  it("shows help text when given and nothing when not", () => {
    field({ fieldId: "f", label: "L", help: "Pick the column being modelled" });
    expect(screen.getByText("Pick the column being modelled")).toBeInTheDocument();

    const { container } = field({ fieldId: "g", label: "M" });
    expect(container.querySelectorAll("p")).toHaveLength(0);
  });

  it("renders whatever control it is given", () => {
    // A slot, not a select: the three objective controls take three different option
    // types, so this wrapper never knows what is inside it.
    field({ fieldId: "family", label: "Family" }, '<select id="family"><option>gamma</option></select>');

    expect(screen.getByLabelText("Family")).toBe(screen.getByRole("combobox"));
  });
});

// NFR-463 / WCAG 1.3.1, 3.3.2 (FD-1974 L-1): help text is only a description if the control
// points at it. The control arrives as a slot, so the field hands the caller the id to bind.
describe("a field's help text is the control's description (FD-1974 L-1)", () => {
  const described = '<template #default="{ describedby }"><input id="response" :aria-describedby="describedby" /></template>';

  it("gives the slot the help id, so the control's accessible description is the help", () => {
    field({ fieldId: "response", label: "Response", help: "Pick the column being modelled" }, described);

    expect(screen.getByLabelText("Response")).toHaveAccessibleDescription("Pick the column being modelled");
  });

  it("hands the slot nothing when there is no help, so no dangling reference is bound", () => {
    field({ fieldId: "response", label: "Response" }, described);

    expect(screen.getByLabelText("Response")).not.toHaveAttribute("aria-describedby");
  });
});
