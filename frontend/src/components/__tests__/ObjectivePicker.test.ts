import { render, screen, waitFor, within } from "@testing-library/vue";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { CustomObjective } from "@/api/objectives";

import ObjectivePicker from "../ObjectivePicker.vue";

const listObjectives = vi.fn();

vi.mock("@/api/objectives", async (importOriginal) => ({
  ...(await importOriginal<object>()),
  listObjectives: () => listObjectives(),
}));

function objective(over: Partial<CustomObjective> = {}): CustomObjective {
  return {
    id: `id-${over.slug ?? "capped"}`,
    slug: "capped-gamma",
    version: 2,
    status: "approved",
    applicability: {
      responses: ["claim_severity"],
      backends: ["xgboost", "lightgbm"],
      offset_required: false,
      y_domain: {},
    },
    ...over,
  } as CustomObjective;
}

function control(): CustomObjective {
  // Applicable under every fixture below. Waiting for it proves the async load has
  // landed, which is what makes a following absence assertion mean anything.
  return objective({ slug: "visible-control", status: "approved" });
}

function picker(props: Record<string, unknown> = {}) {
  return render(ObjectivePicker, {
    props: {
      modelValue: { kind: "builtin", name: "count:poisson" },
      response: "claim_severity",
      backend: "xgboost",
      ...props,
    },
  });
}

const options = () =>
  screen.getAllByRole("option").map((o) => o.textContent?.trim() ?? "");

afterEach(() => vi.clearAllMocks());

describe("the objective picker", () => {
  it("offers the builtins without needing the network", async () => {
    // A custom-objective lookup is not a precondition for choosing a builtin.
    listObjectives.mockRejectedValue(new Error("down"));
    picker();

    await waitFor(() => expect(options()).toContain("count:poisson"));
    expect(options()).toContain("binary:logistic");
    expect(await screen.findByText(/Built-in objectives are unaffected/)).toBeInTheDocument();
  });

  it("offers a custom objective applicable to the response and backend", async () => {
    listObjectives.mockResolvedValue({ items: [objective()], truncated: false });
    picker();

    await waitFor(() => expect(options().join(" ")).toContain("capped-gamma@2"));
  });

  it("withholds one whose applicability excludes the response", async () => {
    // FR-MODEL-44: offering it would manufacture the refusal the requirement prevents.
    listObjectives.mockResolvedValue({
      items: [
        control(),
        objective({ slug: "wrong-response", applicability: {
          responses: ["claim_count"], backends: ["xgboost"],
          offset_required: false, y_domain: {},
        } as CustomObjective["applicability"] }),
      ],
      truncated: false,
    });
    picker({ response: "claim_severity" });

    await waitFor(() => expect(options().join(" ")).toContain("visible-control"));
    expect(options().join(" ")).not.toContain("wrong-response");
  });

  it("withholds one whose applicability excludes the backend", async () => {
    listObjectives.mockResolvedValue({
      items: [
        control(),
        objective({ slug: "wrong-backend", applicability: {
          responses: ["claim_severity"], backends: ["lightgbm"],
          offset_required: false, y_domain: {},
        } as CustomObjective["applicability"] }),
      ],
      truncated: false,
    });
    picker({ backend: "xgboost" });

    await waitFor(() => expect(options().join(" ")).toContain("visible-control"));
    expect(options().join(" ")).not.toContain("wrong-backend");
  });

  it("offers all three fittable statuses, not only approved", async () => {
    // The correction this slice's plan needed: `approved` + `certified` alone would be
    // stricter than the fit, hiding objectives the platform accepts. `review` is in the
    // set and is not a rung between the other two.
    listObjectives.mockResolvedValue({
      items: [
        objective({ slug: "a-certified", status: "certified" }),
        objective({ slug: "b-review", status: "review" }),
        objective({ slug: "c-approved", status: "approved" }),
      ],
      truncated: false,
    });
    picker();

    await waitFor(() => expect(options().join(" ")).toContain("a-certified"));
    expect(options().join(" ")).toContain("b-review");
    expect(options().join(" ")).toContain("c-approved");
  });

  it("withholds draft and deprecated, which no fit accepts", async () => {
    listObjectives.mockResolvedValue({
      items: [
        control(),
        objective({ slug: "d-draft", status: "draft" }),
        objective({ slug: "e-deprecated", status: "deprecated" }),
      ],
      truncated: false,
    });
    picker();

    await waitFor(() => expect(options().join(" ")).toContain("visible-control"));
    expect(options().join(" ")).not.toContain("d-draft");
    expect(options().join(" ")).not.toContain("e-deprecated");
  });

  it("labels the statuses without implying an order between them", async () => {
    // `certified`, `review` and `approved` are a set: `REVIEW → {APPROVED, CERTIFIED}`,
    // so review can return to certified. A label like "almost approved" or a numbered
    // step would be wrong in both directions. The labels are the status names, and the
    // only distinction drawn is approved-or-not, which covers the other two identically.
    listObjectives.mockResolvedValue({
      items: [
        objective({ slug: "a-certified", status: "certified" }),
        objective({ slug: "b-review", status: "review" }),
      ],
      truncated: false,
    });
    picker();

    await waitFor(() => expect(options().join(" ")).toContain("a-certified"));
    const text = document.body.textContent ?? "";
    expect(text).not.toMatch(/almost|nearly|step \d|stage \d|next: /i);
    // One note, not one per status — their relationship to each other is none.
    expect(screen.getAllByText(/cannot be approved until the objective is/)).toHaveLength(1);
  });

  it("says nothing about approval when every option is approved", async () => {
    listObjectives.mockResolvedValue({
      items: [objective({ status: "approved" })],
      truncated: false,
    });
    picker();

    await waitFor(() => expect(options().join(" ")).toContain("capped-gamma"));
    expect(screen.queryByText(/cannot be approved until/)).toBeNull();
  });

  it("says so when the list was truncated", async () => {
    // OQ-MODEL-35: a filtered list presented as complete is the defect. An empty picker
    // must be distinguishable from a picker that stopped looking.
    listObjectives.mockResolvedValue({ items: [objective()], truncated: true });
    picker();

    expect(await screen.findByText(/may be incomplete/)).toBeInTheDocument();
  });

  it("does not warn about truncation when the list is complete", async () => {
    listObjectives.mockResolvedValue({ items: [objective()], truncated: false });
    picker();

    await waitFor(() => expect(options().join(" ")).toContain("capped-gamma"));
    expect(screen.queryByText(/may be incomplete/)).toBeNull();
  });

  it("offers no custom objectives until a response is chosen", async () => {
    // A custom objective with no declared response is itself refused by the validator, so
    // offering one before the response is chosen offers a spec known to be refused.
    listObjectives.mockResolvedValue({ items: [objective()], truncated: false });
    picker({ response: "" });

    // No positive control is possible here — with no response *nothing* custom may show,
    // so the load is synchronised on the mock having been called and settled instead.
    await waitFor(() => expect(listObjectives).toHaveBeenCalled());
    await Promise.resolve();
    await waitFor(() => expect(screen.getByText(/Choose a response/)).toBeInTheDocument());
    expect(options().join(" ")).not.toContain("capped-gamma");
  });

  it("emits a ref for a custom choice and a name for a builtin", async () => {
    // `GbmFunctionRef`'s validator refuses both together: "the fit path would have to
    // choose, and two runs could choose differently".
    const user = userEvent.setup();
    listObjectives.mockResolvedValue({ items: [objective()], truncated: false });
    const { emitted } = picker();

    await waitFor(() => expect(options().join(" ")).toContain("capped-gamma"));
    await user.selectOptions(
      screen.getByRole("combobox"),
      "custom:custom_objective:capped-gamma@2",
    );

    expect(emitted("update:modelValue").at(-1)).toEqual([
      { kind: "custom", ref: "custom_objective:capped-gamma@2" },
    ]);

    await user.selectOptions(screen.getByRole("combobox"), "builtin:reg:gamma");
    expect(emitted("update:modelValue").at(-1)).toEqual([
      { kind: "builtin", name: "reg:gamma" },
    ]);
  });

  it("separates the builtin and custom arms in the list", async () => {
    listObjectives.mockResolvedValue({ items: [objective()], truncated: false });
    const { container } = picker();

    await waitFor(() => expect(options().join(" ")).toContain("capped-gamma"));
    const groups = Array.from(container.querySelectorAll("optgroup"));
    expect(groups.map((g) => g.getAttribute("label"))).toEqual(["Built in", "Custom"]);
    expect(within(groups[1]!).getAllByRole("option")).toHaveLength(1);
  });
});
