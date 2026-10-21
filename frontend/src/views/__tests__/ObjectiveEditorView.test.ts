import { fireEvent, render, screen, waitFor } from "@testing-library/vue";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import * as api from "@/api/objectives";
import type { ObjectivePreview } from "@/api/objectives";
import { ProblemError } from "@/api/problem";

import ObjectiveEditorView from "../ObjectiveEditorView.vue";

// SL-1275 (WK-690 Slice 5), `02` §5.3's Custom objective library editor, against RL-1616's
// preview route (PL-1665 5.3', 5.4). The API is mocked at the wrapper (`@/api/objectives`),
// so these prove the view, not the contract. Every answer is bound to the generated
// `ObjectivePreview` (PL-1665 5.1' landed the shape; the prep's provisional `position` and
// `timeout` fields became the generated `line`, `column` and `reason`).
//
// One parser (PL-1268 Global Constraints): nothing in these tests, or in the view, may parse
// or evaluate the loss. The view's only source of parse errors, derivatives and curve points
// is the mocked API.
vi.mock("vue-echarts", () => ({
  default: { name: "VChart", props: ["option"], template: "<div data-testid='chart' />" },
}));

const LOSS = "w * where(exp(f) < y, w_under, w_over) * (y - exp(f)) ** 2";

function problem(status: number, code: string): ProblemError {
  return new ProblemError({ type: "about:blank", title: code, status, code, errors: [] });
}

function answer(preview: ObjectivePreview): ObjectivePreview {
  return preview;
}

async function typeLoss(text: string) {
  await fireEvent.update(screen.getByRole("textbox", { name: /loss/i }), text);
}

beforeEach(() => vi.useFakeTimers());
afterEach(() => {
  vi.useRealTimers();
  vi.restoreAllMocks();
});

describe("ObjectiveEditorView", () => {
  it("renders the route's parse error at the position it names", async () => {
    // WF-702 B1.5: `numpy.where(...)` is answered 200 with ok false and a positioned error.
    vi.spyOn(api, "previewObjective").mockResolvedValue(
      answer({
        ok: false,
        error: { reason: "grammar", message: "attribute access is not in the grammar", line: 1, column: 5 },
      }),
    );
    render(ObjectiveEditorView);

    await typeLoss("numpy.where(f > y, 1, 2)");
    await vi.advanceTimersByTimeAsync(1000);

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("attribute access is not in the grammar");
    expect(alert).toHaveTextContent(/position\s*5|col(umn)?\s*5/i);
  });

  it("shows the derived gradient and hessian exactly as the API returned them", async () => {
    // B2.4: what the Approver reviews is the derivation, not opaque code. The strings are
    // deliberately ones no client-side differentiation would produce for `LOSS`.
    vi.spyOn(api, "previewObjective").mockResolvedValue(
      answer({ ok: true, gradient: "GRADIENT-FROM-API", hessian: "HESSIAN-FROM-API" }),
    );
    render(ObjectiveEditorView);

    await typeLoss(LOSS);
    await vi.advanceTimersByTimeAsync(1000);

    expect(await screen.findByText("GRADIENT-FROM-API")).toBeInTheDocument();
    expect(screen.getByText("HESSIAN-FROM-API")).toBeInTheDocument();
  });

  it("previews through the API only, debounced: one call for a burst of keystrokes", async () => {
    // RL-1616 Rejected: "A draft per keystroke". Only the stateless preview is called while
    // typing, and not once per keystroke, which would starve the preview executor (3a/3b).
    const preview = vi
      .spyOn(api, "previewObjective")
      .mockResolvedValue(answer({ ok: true }));
    render(ObjectiveEditorView);

    await typeLoss("w");
    await typeLoss("w * f");
    await typeLoss(LOSS);
    expect(preview).not.toHaveBeenCalled();
    await vi.advanceTimersByTimeAsync(1000);

    expect(preview).toHaveBeenCalledTimes(1);
    expect(preview.mock.calls[0]?.[0]).toMatchObject({ loss: LOSS });
  });

  it("disables the editor and says why when the preview answers OBJECTIVE_KIND_NOT_ENABLED", async () => {
    // FR-150 / RL-1616: while `expression_objectives_enabled` is off the answer is 409 with
    // this code. The frontend has no settings read, so the answer is the only signal.
    // PROVISIONAL (flagged for the S5 plan): the 409-driven "disabled while the flag is off"
    // behaviour is not yet ruled; it stands only until the plan settles it.
    vi.spyOn(api, "previewObjective").mockRejectedValue(problem(409, "OBJECTIVE_KIND_NOT_ENABLED"));
    render(ObjectiveEditorView);

    await typeLoss(LOSS);
    await vi.advanceTimersByTimeAsync(1000);

    await waitFor(() => expect(screen.getByRole("textbox", { name: /loss/i })).toBeDisabled());
    expect(screen.getByRole("status")).toHaveTextContent(/expression objectives.*(not enabled|off)/i);
  });

  it("shows a timeout as a preview state, not as a failure of the objective", async () => {
    // Condition 3b: a timeout answers `ok: false` with a timeout reason (not a 500). The
    // loss may be perfectly good; the reader must not be told it is wrong.
    vi.spyOn(api, "previewObjective").mockResolvedValue(
      answer({ ok: false, error: { reason: "timeout", message: "preview timed out" } }),
    );
    render(ObjectiveEditorView);

    await typeLoss(LOSS);
    await vi.advanceTimersByTimeAsync(1000);

    expect(await screen.findByText(/timed out/i)).toBeInTheDocument();
    expect(screen.queryByText(/grammar|invalid loss/i)).not.toBeInTheDocument();
  });

  it("renders a 422 VALIDATION_FAILED (over-bound grid or expression) as its message", async () => {
    // Condition 3a: refused before any SymPy work; the editor shows the platform's detail.
    vi.spyOn(api, "previewObjective").mockRejectedValue(
      new ProblemError({
        type: "about:blank",
        title: "Validation failed",
        status: 422,
        code: "VALIDATION_FAILED",
        detail: "grid exceeds the maximum point count",
        errors: [],
      }),
    );
    render(ObjectiveEditorView);

    await typeLoss(LOSS);
    await vi.advanceTimersByTimeAsync(1000);

    expect(await screen.findByRole("alert")).toHaveTextContent("grid exceeds the maximum point count");
  });

  it("draws the loss curve from the route's points and tabulates them (NFR-463)", async () => {
    vi.spyOn(api, "previewObjective").mockResolvedValue(
      answer({
        ok: true,
        gradient: "g",
        hessian: "h",
        curve: { f: [0, 1], loss: [2.5, 0.5], gradient: [-1, 1], hessian: [2, 2] },
      }),
    );
    render(ObjectiveEditorView);

    await typeLoss(LOSS);
    await vi.advanceTimersByTimeAsync(1000);

    expect(await screen.findByRole("table", { name: /loss curve/i })).toBeInTheDocument();
  });

  it("is create-only: saving creates an expression objective and offers no edit route", async () => {
    // RL-1616 'Editing (need 5.8)': FR-367's "create, edit and version" is met by create,
    // which versions on a reused slug. No edit control and no PATCH/PUT call exist.
    vi.spyOn(api, "previewObjective").mockResolvedValue(answer({ ok: true }));
    const create = vi.spyOn(api, "createObjective").mockResolvedValue(
      { id: "o1" } as unknown as Awaited<ReturnType<typeof api.createObjective>>,
    );
    render(ObjectiveEditorView);

    await typeLoss(LOSS);
    await vi.advanceTimersByTimeAsync(1000);
    await fireEvent.update(screen.getByRole("textbox", { name: /slug/i }), "asymmetric-burning-cost");
    await fireEvent.click(screen.getByRole("button", { name: /create objective/i }));

    expect(create).toHaveBeenCalledTimes(1);
    expect(create.mock.calls[0]?.[0]).toMatchObject({
      kind: "expression",
      slug: "asymmetric-burning-cost",
      loss: LOSS,
    });
    expect(screen.queryByRole("button", { name: /^(edit|update|save draft)/i })).not.toBeInTheDocument();
  });
});
