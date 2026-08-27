import { render, screen, waitFor, within } from "@testing-library/vue";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import ModelSpecBuilderView from "../ModelSpecBuilderView.vue";

const VERSION_ID = "01a0048c-da2f-7513-9de7-0a5e5a9e58cc";

const validateSpec = vi.fn();

vi.mock("@/api/modelSpecs", async (importOriginal) => ({
  ...(await importOriginal<object>()),
  validateSpec: (...args: unknown[]) => validateSpec(...args),
}));

vi.mock("@/api/datasets", () => ({
  listDatasets: async () => ({
    items: [{ id: "ds-1", slug: "fremtpl2", name: "freMTPL2" }],
    next_cursor: null,
    total_estimate: 1,
  }),
  listVersions: async () => ({
    items: [{ id: VERSION_ID, version: 2 }],
    next_cursor: null,
    total_estimate: 1,
  }),
}));

vi.mock("@/api/models", () => ({
  listFactors: async () => [{ id: "f-1", slug: "vehicle_age" }],
}));

vi.mock("@/api/versions", () => ({ listSplits: async () => [] }));

const OK = {
  ok: true,
  problems: [],
  factor_count: 12,
  estimated_parameter_count: 41,
  exposure_per_parameter: 812.5,
};

/** Fill the three fields that gate `spec`, so validation starts firing. */
async function fillRequired(): Promise<void> {
  const user = userEvent.setup();
  render(ModelSpecBuilderView);
  // Wait for the *option*, not the select: the select renders immediately with only its
  // placeholder, so finding it proves nothing about whether the datasets have arrived.
  await screen.findByRole("option", { name: "freMTPL2" });

  await user.selectOptions(screen.getByLabelText("Dataset"), "fremtpl2");
  await screen.findByRole("option", { name: "v2" });
  await user.selectOptions(screen.getByLabelText("Dataset version"), VERSION_ID);
  await user.type(screen.getByLabelText("Model family slug"), "motor-frequency");
  await user.type(screen.getByLabelText("Response column"), "claim_nb");
}

beforeEach(() => {
  vi.useFakeTimers({ shouldAdvanceTime: true });
  validateSpec.mockReset();
  validateSpec.mockResolvedValue(OK);
});

afterEach(() => vi.useRealTimers());

async function settle(): Promise<void> {
  await vi.advanceTimersByTimeAsync(400);
}

describe("the model spec builder", () => {
  it("asks the backend once the spec has its required fields", async () => {
    await fillRequired();
    await settle();

    await waitFor(() => expect(validateSpec).toHaveBeenCalled());
    const sent = validateSpec.mock.calls.at(-1)?.[0] as Record<string, unknown>;
    expect(sent.dataset_version_id).toBe(VERSION_ID);
    expect(sent.model_type).toBe("glm");
  });

  it("coalesces a burst of edits into one request", async () => {
    // Decision 2 chose debounced-live over per-keystroke. Without this the debounce is
    // unasserted: a §13 mutation replacing the `setTimeout` with an immediate call left
    // every other test in this file passing, because they all advance the clock anyway.
    // `fillRequired` types 15 characters into one field and 8 into another, so an
    // undebounced validator issues a request per keystroke.
    await fillRequired();
    await settle();

    await waitFor(() => expect(validateSpec).toHaveBeenCalled());
    expect(validateSpec.mock.calls.length).toBeLessThan(5);
  });

  it("does not ask before the required fields are there", async () => {
    render(ModelSpecBuilderView);
    await screen.findByLabelText("Dataset");
    await settle();

    expect(validateSpec).not.toHaveBeenCalled();
  });

  it("keeps the three objective shapes apart when the tab changes", async () => {
    // Decision 1. A shared "objective" abstraction would carry a value across tabs; these
    // are three different contract shapes, and the GLM arm has no `objective` field at all.
    const user = userEvent.setup();
    await fillRequired();
    await settle();
    expect((validateSpec.mock.calls.at(-1)?.[0] as Record<string, unknown>).objective)
      .toBeUndefined();

    await user.click(screen.getByRole("tab", { name: "GBM" }));
    await settle();
    const gbm = validateSpec.mock.calls.at(-1)?.[0] as Record<string, unknown>;
    expect(gbm.objective).toEqual({ kind: "builtin", name: "count:poisson" });
    expect(gbm.family).toBeUndefined();
    // FR-MODEL-32: `categorical_handling` is required with no default — the GBM arm must
    // name it, and the permissive spec type (OQ-PLAT-16) refuses a body that omits it.
    expect(gbm.categorical_handling).toBe("native");

    await user.click(screen.getByRole("tab", { name: "EBM" }));
    await settle();
    const ebm = validateSpec.mock.calls.at(-1)?.[0] as Record<string, unknown>;
    expect(ebm.objective).toBe("rmse");
    expect(ebm.model_type).toBe("ebm");
  });

  it("renders a refused spec as problems and stays a form", async () => {
    // Branch one: 200 with `ok: false`. `02` §5.1 — "a spec that merely cannot be fitted
    // is not a bad *request*". It must not produce the error surface.
    validateSpec.mockResolvedValue({
      ...OK,
      ok: false,
      problems: [
        { kind: "response_missing", message: "no response column", subject: null },
        { kind: "split_missing", message: "no split named", subject: null },
      ],
    });
    await fillRequired();
    await settle();

    await waitFor(() => expect(screen.getByText("no response column")).toBeInTheDocument());
    expect(screen.getByText("no split named")).toBeInTheDocument();
    expect(screen.queryByRole("alert")).toBeNull();
  });

  it("renders a 422 from its field errors, not from its generic title", async () => {
    // Branch two, and the measured one. A spec the *type* refuses comes back 422 with
    // `title: "Request validation failed"` and `detail: "1 field(s) failed validation."`
    // — both useless — while the sentence that names the problem is only in `errors[]`.
    const { ProblemError } = await import("@/api/problem");
    validateSpec.mockRejectedValue(new ProblemError({
      type: "https://docs.gi-pricing.dev/errors/validation-failed",
      title: "Request validation failed",
      status: 422,
      code: "VALIDATION_FAILED",
      detail: "1 field(s) failed validation.",
      errors: [{
        field: "spec.glm",
        code: "VALUE_ERROR",
        message: "Value error, a Poisson model must declare an offset (FR-MODEL-19).",
      }],
      trace_id: "abc123",
    }));
    await fillRequired();
    await settle();

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("a Poisson model must declare an offset");
    // The generic pair must not be what the analyst is shown.
    expect(alert).not.toHaveTextContent("1 field(s) failed validation");
  });

  it("renders a 404 from its title and detail, since it carries no field errors", async () => {
    // Branch three. Distinct from the 422 above: same error class, different payload
    // shape, and rendering one as the other tells the analyst the version is missing when
    // the answer was "this family needs an offset" — or the reverse.
    const { ProblemError } = await import("@/api/problem");
    validateSpec.mockRejectedValue(new ProblemError({
      type: "https://docs.gi-pricing.dev/errors/not-found",
      title: "Not found",
      status: 404,
      code: "DATASET_VERSION_NOT_FOUND",
      detail: "No such dataset version",
      errors: [],
      trace_id: "def456",
    }));
    await fillRequired();
    await settle();

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Not found");
    expect(alert).toHaveTextContent("No such dataset version");
    expect(alert).not.toHaveTextContent("cannot be stored");
  });

  it("shows the complexity diagnostic even when the spec is fine", async () => {
    // FR-MODEL-81: complexity is "a diagnostic by default, and a gate only where a
    // workspace asks for one". Both limits are unset unless a workspace sets them, so in
    // a default workspace no `complexity_limit` problem is raised and `ok` stays true —
    // a block drawn only when `ok` is false would show this never, in exactly the
    // configuration the requirement is about.
    await fillRequired();
    await settle();

    await waitFor(() => expect(screen.getByText("This spec may be fitted.")).toBeInTheDocument());

    // Scoped to the diagnostic block: "Factors" is also the multi-select's label, and an
    // unscoped `getByText` matched both — which would have let this pass on the form
    // control while the diagnostic was absent.
    const complexity = within(screen.getByLabelText("Complexity"));
    expect(complexity.getByText("12")).toBeInTheDocument();
    expect(complexity.getByText("41")).toBeInTheDocument();
    expect(complexity.getByText("812.5")).toBeInTheDocument();
  });

  it("shows a threshold only where the workspace set one", async () => {
    validateSpec.mockResolvedValue({ ...OK, max_factor_count: 30 });
    await fillRequired();
    await settle();

    await waitFor(() => expect(screen.getByText(/\/ 30/)).toBeInTheDocument());
  });

  it("does not let a slow earlier response overwrite a fast later one", async () => {
    // The stale-problems defect a debounced validator has without a sequence guard: an
    // analyst edits against problems belonging to a spec they have already changed.
    const user = userEvent.setup();
    let releaseFirst: (v: unknown) => void = () => {};
    validateSpec
      .mockImplementationOnce(() => new Promise((resolve) => { releaseFirst = resolve; }))
      .mockResolvedValue({ ...OK, ok: true });

    await fillRequired();
    await settle();

    await user.click(screen.getByRole("tab", { name: "EBM" }));
    await settle();
    await waitFor(() => expect(screen.getByText("This spec may be fitted.")).toBeInTheDocument());

    // The first request now lands, carrying problems for the spec that was superseded.
    releaseFirst({
      ...OK, ok: false,
      problems: [{ kind: "response_missing", message: "stale problem", subject: null }],
    });
    await settle();

    expect(screen.queryByText("stale problem")).toBeNull();
    expect(screen.getByText("This spec may be fitted.")).toBeInTheDocument();
  });
});
