import userEvent from "@testing-library/user-event";
import { render, screen } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import NodeNavigator from "../NodeNavigator.vue";
import { valid } from "./fixtures";

function mount(selected: string | null = null) {
  const view = render(NodeNavigator, { props: { steps: valid.steps, selected } });
  const list = screen.getByRole("listbox", { name: "Steps in graph order" });
  return { ...view, list };
}

const active = (list: HTMLElement): string | null => list.getAttribute("aria-activedescendant");

describe("the keyboard node navigator (RS-1269 F2 condition 2)", () => {
  it("lists one option per step, in graph order", () => {
    mount();
    const options = screen.getAllByRole("option").map((o) => o.id);
    expect(options[0]).toBe("nav-s_in_age");
    expect(options).toHaveLength(valid.steps.length);
  });

  it("moves through the steps with the arrow keys", async () => {
    const { list } = mount();
    await userEvent.click(list);
    expect(active(list)).toBe("nav-s_in_age");
    await userEvent.keyboard("{ArrowDown}");
    expect(active(list)).toBe("nav-s_in_eff");
    await userEvent.keyboard("{ArrowDown}{ArrowUp}");
    expect(active(list)).toBe("nav-s_in_eff");
  });

  it("jumps to the first and last step with Home and End", async () => {
    const { list } = mount();
    await userEvent.click(list);
    await userEvent.keyboard("{End}");
    expect(active(list)).toBe("nav-s_out");
    await userEvent.keyboard("{Home}");
    expect(active(list)).toBe("nav-s_in_age");
  });

  it("jumps to a step by typing a step_id prefix", async () => {
    const { list } = mount();
    await userEvent.click(list);
    await userEvent.keyboard("s_pay");
    expect(active(list)).toBe("nav-s_payable");
  });

  it("selects the active step on Enter", async () => {
    const { list, emitted } = mount();
    await userEvent.click(list);
    await userEvent.keyboard("{ArrowDown}{ArrowDown}{Enter}");
    expect(emitted()["select"]).toEqual([["s_in_channel"]]);
  });

  it("asks before removing a step on Delete", async () => {
    const { list, emitted } = mount();
    await userEvent.click(list);
    await userEvent.keyboard("{ArrowDown}{Delete}");
    const dialog = screen.getByRole("alertdialog");
    expect(dialog).toHaveTextContent("s_in_eff");
    expect(emitted()["remove"]).toBeUndefined();

    await userEvent.click(screen.getByRole("button", { name: "Cancel" }));
    expect(screen.queryByRole("alertdialog")).toBeNull();
    expect(emitted()["remove"]).toBeUndefined();

    await userEvent.keyboard("{Delete}");
    await userEvent.click(screen.getByRole("button", { name: "Remove step" }));
    expect(emitted()["remove"]).toEqual([["s_in_eff"]]);
  });

  it("4.1.3: a removal is announced, and the active option moves to the neighbour", async () => {
    const { list, emitted, rerender } = mount();
    await userEvent.click(list);
    await userEvent.keyboard("{ArrowDown}{Delete}");
    await userEvent.click(screen.getByRole("button", { name: "Remove step" }));
    expect(emitted()["remove"]).toEqual([["s_in_eff"]]);
    expect(screen.getByRole("status")).toHaveTextContent("Removed step s_in_eff");
    await rerender({ steps: valid.steps.filter((s) => s.step_id !== "s_in_eff"), selected: null });
    expect(active(list)).toBe("nav-s_in_channel");
  });

  it("1.4.1: the selected option carries a non-colour marker", () => {
    mount("s_area");
    expect(document.getElementById("nav-s_area")).toHaveClass("font-semibold", "border-sky-700");
    expect(document.getElementById("nav-s_in_age")).not.toHaveClass("font-semibold");
  });
});
