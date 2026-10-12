import userEvent from "@testing-library/user-event";
import { render, screen, within } from "@testing-library/vue";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ProblemError } from "@/api/problem";

import QuoteSandboxView from "../QuoteSandboxView.vue";

const getRatingVersionByRef = vi.fn();
const getRatingAlgorithm = vi.fn();
const scoreQuote = vi.fn();

vi.mock("@/api/ratingVersions", () => ({
  getRatingVersionByRef: (...args: unknown[]) => getRatingVersionByRef(...args),
}));
vi.mock("@/api/ratingAlgorithms", () => ({
  getRatingAlgorithm: (...args: unknown[]) => getRatingAlgorithm(...args),
}));
vi.mock("@/api/score", () => ({
  scoreQuote: (...args: unknown[]) => scoreQuote(...args),
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
    steps: [{ step_id: "s_in", type: "input", label: "Driver age", consumed: {}, produced: { driver_age: 34 } }],
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

function problem(status: number, code: string, detail: string): ProblemError {
  return new ProblemError({ type: "about:blank", title: "Refused", status, code, detail, errors: [] });
}

beforeEach(() => {
  getRatingVersionByRef.mockResolvedValue(RATING);
  getRatingAlgorithm.mockResolvedValue(ALGORITHM);
  scoreQuote.mockResolvedValue(RESULT);
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
});
