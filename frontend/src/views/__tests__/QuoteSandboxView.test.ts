import userEvent from "@testing-library/user-event";
import { render, screen, waitFor, within } from "@testing-library/vue";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ProblemError } from "@/api/problem";
import type { ScoreComparison } from "@/api/score";

import QuoteSandboxView from "../QuoteSandboxView.vue";

const getRatingVersionByRef = vi.fn();
const listRatingVersions = vi.fn();
const getRatingAlgorithm = vi.fn();
const scoreQuote = vi.fn();
const scoreCompare = vi.fn();

vi.mock("@/api/ratingVersions", () => ({
  getRatingVersionByRef: (...args: unknown[]) => getRatingVersionByRef(...args),
  listRatingVersions: (...args: unknown[]) => listRatingVersions(...args),
}));
vi.mock("@/api/ratingAlgorithms", () => ({
  getRatingAlgorithm: (...args: unknown[]) => getRatingAlgorithm(...args),
}));
vi.mock("@/api/score", () => ({
  scoreQuote: (...args: unknown[]) => scoreQuote(...args),
  scoreCompare: (...args: unknown[]) => scoreCompare(...args),
}));
vi.mock("vue-echarts", () => ({
  default: { name: "VChart", props: ["option"], template: "<div data-testid='chart' />" },
}));

const RATING = {
  id: "01a04394-338b-7651-9e42-c73ee70396f8",
  slug: "motor-gb",
  version: 3,
  status: "draft",
  algorithm_ref: "rating_algorithm:motor-gb@2",
};

const OTHER = {
  ...RATING,
  id: "01a04394-338b-7651-9e42-c73ee70396f9",
  version: 2,
  status: "approved",
};

const ALGORITHM = {
  slug: "motor-gb",
  version: 2,
  input_contract: [
    { name: "driver_age", type: "int", nullable: false, min: 17, max: 99 },
    { name: "channel", type: "enum", nullable: false, domain: ["direct", "broker"] },
  ],
  outputs: [],
  steps: [],
  sub_graphs: [],
};

const RESULT = {
  outcome: "quoted",
  rating_version_ref: "rating_version:motor-gb@3",
  bundle_hash: `sha256:${"c".repeat(64)}`,
  outputs: { payable_premium_minor: 63000 },
  premium_ladder: [
    { rung: "risk_premium", value_minor: 50000 },
    { rung: "payable_premium", value_minor: 63000, operation: { kind: "multiply", factor: "1.26" } },
  ],
  trace: {
    rating_version_ref: "rating_version:motor-gb@3",
    bundle_hash: `sha256:${"c".repeat(64)}`,
    ladder_reconciled: true,
    steps: [{ step_id: "s_in", type: "input", label: "Driver age", elapsed_us: 0, consumed: {}, produced: { driver_age: 34 } }],
  },
};

const COMPARISON: ScoreComparison = {
  base: RESULT as ScoreComparison["base"],
  comparison: {
    ...(RESULT as ScoreComparison["comparison"]),
    rating_version_ref: "rating_version:motor-gb@2",
    premium_ladder: [
      { rung: "risk_premium", value_minor: 48000 },
      { rung: "payable_premium", value_minor: 60000 },
    ],
  },
  diff: {
    unchanged: 1,
    steps: [
      {
        step_id: "s_rate",
        change: "changed",
        own_change: true,
        changed_fields: ["produced"],
        base: { step_id: "s_rate", type: "table", label: "Rate", elapsed_us: 0, consumed: {}, produced: { rate: "1.10" } },
        comparison: { step_id: "s_rate", type: "table", label: "Rate", elapsed_us: 0, consumed: {}, produced: { rate: "1.20" } },
      },
    ],
  },
};

const props = { slug: "motor-gb", version: "3" };
const mounted = {
  global: { stubs: { RouterLink: { props: ["to"], template: '<a :href="to"><slot /></a>' } } },
};

async function fillAndSubmit(age = "34"): Promise<void> {
  await userEvent.type(await screen.findByLabelText("driver_age"), age);
  await userEvent.selectOptions(screen.getByLabelText("channel"), "direct");
  await userEvent.click(screen.getByRole("button", { name: "Score quote" }));
}

/** Choose the comparison version in the picker; red until the picker exists (PL-1764 Task 2). */
async function pickComparison(): Promise<void> {
  await waitFor(() => expect(screen.queryByLabelText("Compare against")).not.toBeNull());
  await waitFor(() => expect(screen.queryByRole("option", { name: "motor-gb@2 · approved" })).not.toBeNull());
  await userEvent.selectOptions(screen.getByLabelText("Compare against"), "motor-gb@2 · approved");
}

function problem(status: number, code: string, detail: string): ProblemError {
  return new ProblemError({ type: "about:blank", title: "Refused", status, code, detail, errors: [] });
}

beforeEach(() => {
  getRatingVersionByRef.mockResolvedValue(RATING);
  getRatingAlgorithm.mockResolvedValue(ALGORITHM);
  scoreQuote.mockResolvedValue(RESULT);
  listRatingVersions.mockResolvedValue([RATING, OTHER]);
  scoreCompare.mockResolvedValue(COMPARISON);
});
afterEach(() => vi.clearAllMocks());

describe("the quote sandbox view", () => {
  it("resolves the version by the slug and version of the URL and loads the algorithm it pins", async () => {
    render(QuoteSandboxView, { props, ...mounted });
    await screen.findByLabelText("driver_age");
    expect(getRatingVersionByRef).toHaveBeenCalledWith("motor-gb", 3);
    expect(getRatingAlgorithm).toHaveBeenCalledWith("motor-gb", 2);
  });

  it("FR-213: builds one control per declared input", async () => {
    render(QuoteSandboxView, { props, ...mounted });
    expect(await screen.findByLabelText("driver_age")).toBeInTheDocument();
    const channel = screen.getByLabelText("channel");
    expect(within(channel).getAllByRole("option").map((o) => o.textContent?.trim())).toEqual([
      "Choose…",
      "direct",
      "broker",
    ]);
  });

  it("FR-251: scores the version in view through an explicit rating_version_ref, as what_if, with a trace", async () => {
    render(QuoteSandboxView, { props, ...mounted });
    await fillAndSubmit();
    await screen.findByTestId("outcome");
    const [body] = scoreQuote.mock.calls[0] as [Record<string, unknown>];
    expect(body["purpose"]).toBe("what_if");
    expect(body["inputs"]).toEqual({ driver_age: 34, channel: "direct" });
    expect(body["options"]).toEqual({ rating_version_ref: "rating_version:motor-gb@3", trace: true });
  });

  it("FR-247, FR-258, FR-25: shows the outcome, the ladder and the trace together, no click between", async () => {
    render(QuoteSandboxView, { props, ...mounted });
    await fillAndSubmit();
    expect(await screen.findByTestId("outcome")).toHaveTextContent("quoted");
    expect(screen.getByRole("table", { name: /premium ladder/i })).toBeInTheDocument();
    expect(screen.getByRole("list", { name: "Trace steps" })).toBeInTheDocument();
  });

  it("FR-256: a declined quote is a result, its reasons listed and its ladder still shown", async () => {
    scoreQuote.mockResolvedValue({ ...RESULT, outcome: "declined", decline_reasons: ["AGE_BELOW_MIN"] });
    render(QuoteSandboxView, { props, ...mounted });
    await fillAndSubmit("17");
    expect(await screen.findByTestId("outcome")).toHaveTextContent("declined");
    expect(screen.getByLabelText("Decline reasons")).toHaveTextContent("AGE_BELOW_MIN");
    expect(screen.getByRole("table", { name: /premium ladder/i })).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it.each([
    [422, "INPUT_CONTRACT_VIOLATION", "Contract violation"],
    [422, "REFERENCE_LOOKUP_MISS", "Reference miss"],
    [422, "RATE_TABLE_MISS", "Table miss"],
    [422, "MODEL_CALL_FAILED", "Model failure"],
  ])("FR-255: %s %s renders as %s and replaces any earlier result", async (status, code, heading) => {
    render(QuoteSandboxView, { props, ...mounted });
    await fillAndSubmit();
    await screen.findByTestId("outcome");

    scoreQuote.mockRejectedValue(problem(status, code, "detail from the platform"));
    await userEvent.click(screen.getByRole("button", { name: "Score quote" }));
    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent(heading);
    expect(alert).toHaveTextContent("detail from the platform");
    expect(screen.queryByTestId("outcome")).not.toBeInTheDocument();
  });

  it("does not call the platform while a field cannot be typed", async () => {
    render(QuoteSandboxView, { props, ...mounted });
    await userEvent.type(await screen.findByLabelText("driver_age"), "abc");
    await userEvent.click(screen.getByRole("button", { name: "Score quote" }));
    expect(await screen.findByText("Enter a whole number")).toBeInTheDocument();
    expect(scoreQuote).not.toHaveBeenCalled();
  });

  it("FR-249 (R6.1, OQ-1460): states that per-peril components are absent", async () => {
    render(QuoteSandboxView, { props, ...mounted });
    await fillAndSubmit();
    expect(await screen.findByTestId("per-peril-absent")).toHaveTextContent(/not available/i);
  });

  it("says so when the version pins no algorithm, and builds no form", async () => {
    getRatingVersionByRef.mockResolvedValue({ ...RATING, algorithm_ref: null });
    render(QuoteSandboxView, { props, ...mounted });
    expect(await screen.findByText(/pins no algorithm/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Score quote" })).not.toBeInTheDocument();
  });

  it("shows a refused load with its title and detail", async () => {
    getRatingVersionByRef.mockRejectedValue(problem(404, "NOT_FOUND", "no such version"));
    render(QuoteSandboxView, { props, ...mounted });
    expect(await screen.findByRole("alert")).toHaveTextContent("no such version");
  });

  // PL-1764 Task 2 and Task 3 (SL-1550, WK-675 lane C S7), with RL-1765 DP-1 (a).
  it("FR-262 C1 (RL-1765 DP-1): the picker excludes the version in view and offers 'No comparison' first", async () => {
    render(QuoteSandboxView, { props, ...mounted });
    await screen.findByLabelText("driver_age");
    const picker = screen.queryByLabelText("Compare against");
    expect(picker).not.toBeNull();
    await waitFor(() =>
      expect(within(picker!).getAllByRole("option").map((o) => o.textContent?.trim())).toEqual([
        "No comparison",
        "motor-gb@2 · approved",
      ]),
    );
  });

  it("FR-262 C2: a chosen comparison scores one quote against two versions, with no options in context", async () => {
    render(QuoteSandboxView, { props, ...mounted });
    await screen.findByLabelText("driver_age");
    await pickComparison();
    await fillAndSubmit();
    await waitFor(() => expect(scoreCompare).toHaveBeenCalledTimes(1));
    const [body] = scoreCompare.mock.calls[0] as [Record<string, unknown>];
    expect(body["base"]).toBe("rating_version:motor-gb@3");
    expect(body["comparison"]).toBe("rating_version:motor-gb@2");
    const context = body["context"] as Record<string, unknown>;
    expect(context["purpose"]).toBe("what_if");
    expect(context["inputs"]).toEqual({ driver_age: 34, channel: "direct" });
    expect(context).not.toHaveProperty("options");
    expect(scoreQuote).not.toHaveBeenCalled();
  });

  it("FR-262 C3: a per-quote error on the comparison side shows its detail, which names the side", async () => {
    scoreCompare.mockRejectedValue(
      problem(422, "INPUT_CONTRACT_VIOLATION", "comparison: driver_age is above its max"),
    );
    render(QuoteSandboxView, { props, ...mounted });
    await screen.findByLabelText("driver_age");
    await pickComparison();
    await fillAndSubmit();
    await waitFor(() =>
      expect(screen.queryByRole("alert")).toHaveTextContent("comparison: driver_age is above its max"),
    );
  });

  it("FR-262 C4: the compare panel mounts under the trace, beside one outcome from the base side", async () => {
    render(QuoteSandboxView, { props, ...mounted });
    await screen.findByLabelText("driver_age");
    await pickComparison();
    await fillAndSubmit();
    await waitFor(() =>
      expect(screen.queryByRole("region", { name: /Compared with rating_version:motor-gb@2/ })).not.toBeNull(),
    );
    expect(screen.queryByTestId("outcome")).toHaveTextContent("quoted");
  });

  it("FR-262 C5 (guard, green on arrival): with no comparison chosen the view scores through scoreQuote only", async () => {
    render(QuoteSandboxView, { props, ...mounted });
    await fillAndSubmit();
    await waitFor(() => expect(scoreQuote).toHaveBeenCalledTimes(1));
    expect(scoreCompare).not.toHaveBeenCalled();
  });

  it("FR-262 C6: a refused version list is said so and leaves the sandbox usable", async () => {
    listRatingVersions.mockRejectedValue(problem(403, "WORKSPACE_SCOPE_DENIED", "no access"));
    render(QuoteSandboxView, { props, ...mounted });
    await screen.findByLabelText("driver_age");
    await waitFor(() =>
      expect(screen.queryByText(/Versions to compare against could not be loaded/)).not.toBeNull(),
    );
    expect(screen.getByRole("button", { name: "Score quote" })).toBeEnabled();
  });
});

// NFR-463 / WCAG 4.1.3 (FD-1959 M4): a status message is announced only if its live region is in
// the DOM before the message arrives. A region that mounts together with its text (v-if) is not.
const liveRegions = (root: Element): Element[] =>
  Array.from(root.querySelectorAll('[role="status"], [aria-live="polite"]'));

describe("the quote sandbox view: the result is announced (NFR-463, FD-1959 M4)", () => {
  it("announces the score in a region that was already there, or by moving focus into the result", async () => {
    const { container } = render(QuoteSandboxView, { props, ...mounted });
    await screen.findByLabelText("driver_age");
    const before = liveRegions(container);
    await fillAndSubmit();
    const outcome = await screen.findByTestId("outcome");
    const holder = liveRegions(container).find((el) => /quoted/i.test(el.textContent ?? ""));
    const focusInResult = outcome.parentElement?.contains(document.activeElement) === true
      && document.activeElement !== document.body;
    const announced = (holder !== undefined && before.includes(holder)) || focusInResult;
    expect(announced).toBe(true);
  });
});
