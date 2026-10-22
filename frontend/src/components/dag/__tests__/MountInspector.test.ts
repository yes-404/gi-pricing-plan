// RL-1835 (i) 5, (iii) 1-2: the inspector edits a mount from the fragment's own ports.
import userEvent from "@testing-library/user-event";
import { render, screen, within } from "@testing-library/vue";
import { beforeEach, describe, expect, it, vi } from "vitest";

import MountInspector from "../MountInspector.vue";
import { FEES, FRAGMENT, PINS, REFUND } from "./mountFixtures";

const api = vi.hoisted(() => ({ getSubGraph: vi.fn() }));
vi.mock("@/api/subGraphs", () => api);

beforeEach(() => {
  api.getSubGraph.mockReset();
  api.getSubGraph.mockResolvedValue(FRAGMENT);
});

const last = (emitted: Record<string, unknown[][]>): Record<string, unknown> =>
  (emitted["update:mount"] ?? []).at(-1)?.[0] as Record<string, unknown>;

describe("the mount inspector", () => {
  it("shows exactly the fragment's input ports, read through the generated type", async () => {
    render(MountInspector, { props: { mount: FEES, subGraphPins: PINS } });
    const group = await screen.findByRole("group", { name: "Input ports" });
    const labels = (await within(group).findAllByRole("textbox")).map((box) => box.getAttribute("aria-label"));
    expect(labels).toEqual(["Input base (money_minor)", "Input rate (decimal)"]);
    expect(api.getSubGraph).toHaveBeenCalledWith("ipt-and-fees", 1);
  });

  it("offers one output row per output port, each optional", async () => {
    const { emitted } = render(MountInspector, { props: { mount: FEES, subGraphPins: PINS } });
    const group = await screen.findByRole("group", { name: "Output ports" });
    const ipt = await within(group).findByLabelText("Output ipt (money_minor)");
    await userEvent.type(ipt, "i");
    expect((last(emitted() as Record<string, unknown[][]>)["outputs"] as Record<string, string>)["ipt"]).toBe("i");
    await userEvent.clear(ipt);
    expect(last(emitted() as Record<string, unknown[][]>)["outputs"]).toEqual({ total: "fees_total" });
  });

  it("omits purposes when neither box is checked, never sending an empty list", async () => {
    const { emitted } = render(MountInspector, { props: { mount: REFUND, subGraphPins: PINS } });
    const box = await screen.findByLabelText("cancellation");
    expect(box).toBeChecked();
    await userEvent.click(box);
    const mount = last(emitted() as Record<string, unknown[][]>);
    expect("purposes" in mount).toBe(false);
  });

  it("sends both purposes in canonical order when both boxes are checked", async () => {
    const { emitted } = render(MountInspector, { props: { mount: REFUND, subGraphPins: PINS } });
    await userEvent.click(await screen.findByLabelText("mid_term_adjustment"));
    expect(last(emitted() as Record<string, unknown[][]>)["purposes"]).toEqual([
      "mid_term_adjustment",
      "cancellation",
    ]);
  });

  it("offers exactly the Rating Version's sub-graph pins as the version options", async () => {
    render(MountInspector, { props: { mount: FEES, subGraphPins: PINS } });
    const select = await screen.findByLabelText("Sub-graph version");
    const options = within(select).getAllByRole("option").map((o) => o.getAttribute("value"));
    expect(options).toEqual(PINS);
  });

  it("emits the picked pin as the mount's ref", async () => {
    const { emitted } = render(MountInspector, { props: { mount: FEES, subGraphPins: PINS } });
    await userEvent.selectOptions(await screen.findByLabelText("Sub-graph version"), REFUND.ref);
    expect(last(emitted() as Record<string, unknown[][]>)["ref"]).toBe(REFUND.ref);
  });

  it("resets the port maps when the pick has another slug (the slice's choice, RS 8156 (v))", async () => {
    const { emitted } = render(MountInspector, { props: { mount: FEES, subGraphPins: PINS } });
    await userEvent.selectOptions(await screen.findByLabelText("Sub-graph version"), REFUND.ref);
    const mount = last(emitted() as Record<string, unknown[][]>);
    expect(mount["ref"]).toBe(REFUND.ref);
    expect(mount["inputs"]).toEqual({});
    expect(mount["outputs"]).toEqual({});
  });

  it("keeps the port maps when the pick is another version of the same slug", async () => {
    const v2 = "sub_graph:ipt-and-fees@2";
    const { emitted } = render(MountInspector, { props: { mount: FEES, subGraphPins: [FEES.ref, v2] } });
    await userEvent.selectOptions(await screen.findByLabelText("Sub-graph version"), v2);
    const mount = last(emitted() as Record<string, unknown[][]>);
    expect(mount["ref"]).toBe(v2);
    expect(mount["inputs"]).toEqual(FEES.inputs);
    expect(mount["outputs"]).toEqual(FEES.outputs);
  });
});
