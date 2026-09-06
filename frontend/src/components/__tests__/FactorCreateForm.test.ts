import { render, screen, waitFor } from "@testing-library/vue";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import FactorCreateForm from "../FactorCreateForm.vue";

const createFactor = vi.fn();

vi.mock("@/api/models", async (importOriginal) => ({
  ...(await importOriginal<object>()),
  createFactor: (body: unknown) => createFactor(body),
}));

function form() {
  return render(FactorCreateForm, {
    props: { datasetId: "ds-1", columns: ["vehicle_age", "area"] },
  });
}

afterEach(() => vi.clearAllMocks());

describe("creating a factor", () => {
  it("offers only the intents the platform still honours", () => {
    // `offset` and `diagnostic` are superseded (FR-84, FR-86) and keep their
    // arm in the contract deliberately. Offering them would produce a factor that is
    // accepted, stored and audited, then refused at fit — `POST /factors` has no such
    // check, so this control is the guard.
    form();
    const options = screen.getAllByRole("option").map((o) => o.textContent?.trim() ?? "");

    expect(options.join(" ")).toContain("Risk");
    expect(options.join(" ")).toContain("Control");
    expect(options.join(" ")).not.toContain("Offset");
    expect(options.join(" ")).not.toContain("Diagnostic");
  });

  it("says the intent is set once, because it is", () => {
    // A Factor is frozen and `/factors` has no PATCH; a repeated slug versions rather than
    // edits. Telling the actuary beats letting them discover it.
    form();

    expect(screen.getByText(/cannot be changed afterwards/)).toBeInTheDocument();
  });

  it("asks for no rationale while the direction is none", () => {
    form();

    expect(screen.queryByLabelText(/Why this direction/)).toBeNull();
  });

  it("requires a rationale once a direction is chosen, before sending anything", async () => {
    // FR-89's rule is enforced by `Factor`'s own validator, so without this the answer
    // is a 422 rather than a disabled button. The request must not be made at all.
    const user = userEvent.setup();
    form();

    await user.selectOptions(screen.getByLabelText("Column"), "vehicle_age");
    await user.type(screen.getByLabelText("Slug"), "vehicle-age-band");
    await user.selectOptions(screen.getByLabelText(/Monotonic direction/), "increasing");

    expect(screen.getByLabelText(/Why this direction/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Create factor/ })).toBeDisabled();

    await user.click(screen.getByRole("button", { name: /Create factor/ }));
    expect(createFactor).not.toHaveBeenCalled();
  });

  it("sends the rationale with the direction it justifies", async () => {
    const user = userEvent.setup();
    createFactor.mockResolvedValue({ slug: "vehicle-age-band", version: 1 });
    form();

    await user.selectOptions(screen.getByLabelText("Column"), "vehicle_age");
    await user.type(screen.getByLabelText("Slug"), "vehicle-age-band");
    await user.selectOptions(screen.getByLabelText(/Monotonic direction/), "increasing");
    await user.type(screen.getByLabelText(/Why this direction/), "older vehicles claim more");
    await user.click(screen.getByRole("button", { name: /Create factor/ }));

    await waitFor(() => expect(createFactor).toHaveBeenCalled());
    expect(createFactor.mock.calls[0]?.[0]).toMatchObject({
      slug: "vehicle-age-band",
      dataset_id: "ds-1",
      source_columns: ["vehicle_age"],
      intent: "risk",
      monotonic_direction: "increasing",
      monotonic_rationale: "older vehicles claim more",
    });
  });

  it("omits the rationale rather than sending an empty one when there is no direction", async () => {
    // `monotonic_rationale` is `str | None`; "" is a rationale that says nothing, and a
    // stored empty string reads as one somebody wrote.
    const user = userEvent.setup();
    createFactor.mockResolvedValue({ slug: "area-factor", version: 1 });
    form();

    await user.selectOptions(screen.getByLabelText("Column"), "area");
    await user.type(screen.getByLabelText("Slug"), "area-factor");
    await user.click(screen.getByRole("button", { name: /Create factor/ }));

    await waitFor(() => expect(createFactor).toHaveBeenCalled());
    expect(createFactor.mock.calls[0]?.[0]).not.toHaveProperty("monotonic_rationale");
  });

  it("renders a refusal's field errors rather than its generic title", async () => {
    // The W6b-4a lesson: a 422's actionable sentence lives only in `errors[]`, and the
    // house title/detail pair is boilerplate.
    const user = userEvent.setup();
    const { ProblemError } = await import("@/api/problem");
    createFactor.mockRejectedValue(new ProblemError({
      type: "https://docs.gi-pricing.dev/errors/validation-failed",
      title: "Request validation failed",
      status: 422,
      code: "VALIDATION_FAILED",
      detail: "1 field(s) failed validation.",
      errors: [{ field: "body", code: "VALUE_ERROR", message: "slug already versioned" }],
      trace_id: "t1",
    }));
    form();

    await user.selectOptions(screen.getByLabelText("Column"), "area");
    await user.type(screen.getByLabelText("Slug"), "area-factor");
    await user.click(screen.getByRole("button", { name: /Create factor/ }));

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("slug already versioned");
    expect(alert).not.toHaveTextContent("1 field(s) failed validation");
  });
});
