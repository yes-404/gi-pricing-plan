import userEvent from "@testing-library/user-event";
import { render, screen, waitFor, within } from "@testing-library/vue";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import ValidationReportView from "../ValidationReportView.vue";

/**
 * Shaped on freMTPL2 v1 as the platform actually reports it: `exposure-plausible` fails on
 * 571 rows, `severity-outlier` warns on 125 claims, `vehicle-brand-mix` skips for want of
 * a reference version. Using the real report means the view is tested against what the
 * backend emits rather than against what a fixture author imagined.
 */
const EXPOSURE_RULE = "11111111-1111-4111-8111-111111111111";
const SEVERITY_RULE = "22222222-2222-4222-8222-222222222222";

const REPORT = {
  id: "33333333-3333-4333-8333-333333333333",
  dataset_version_id: "44444444-4444-4444-8444-444444444444",
  rule_set_id: "55555555-5555-4555-8555-555555555555",
  rule_set_version: 1,
  started_at: "2026-08-15T09:00:00Z",
  finished_at: "2026-08-15T09:00:01Z",
  empty_layers: [],
  results: [
    {
      rule_id: EXPOSURE_RULE,
      rule_slug: "exposure-plausible",
      rule_version: 1,
      layer: "actuarial_sanity",
      severity: "fail",
      outcome: "fail",
      measured: { violating_rows: 571 },
      threshold: { max_inclusive: 1.05 },
      affected_rows: 571,
      detail: "571 row(s) outside the declared range for 'exposure_years'",
      offending_sample: [{ policy_id: "P1" }, { policy_id: "P2" }],
    },
    {
      rule_id: SEVERITY_RULE,
      rule_slug: "severity-outlier",
      rule_version: 1,
      layer: "actuarial_sanity",
      severity: "warn",
      outcome: "warn",
      measured: { large_losses: 125 },
      threshold: { percentile: 0.995 },
      affected_rows: 125,
      detail: "125 claim(s) at or above 3,563,033 minor units — flagged, not removed",
      offending_sample: [],
    },
    {
      rule_id: "66666666-6666-4666-8666-666666666666",
      rule_slug: "columns-present",
      rule_version: 1,
      layer: "structural",
      severity: "fail",
      outcome: "pass",
      measured: {},
      threshold: {},
      detail: "",
      offending_sample: [],
    },
  ],
};

function route(url: string): unknown {
  if (url.includes("/versions/1")) return { id: REPORT.dataset_version_id, version: 1 };
  if (url.includes("/validation-reports") && !url.includes("/validation-reports/")) {
    return [{ id: REPORT.id, unacknowledged_warnings: 1 }];
  }
  return REPORT;
}

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: string | URL) =>
      new Response(JSON.stringify(route(String(input))), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    ),
  );
});
afterEach(() => vi.unstubAllGlobals());

const props = { slug: "fremtpl2", version: "1" };

describe("the validation report view", () => {
  it("answers 'why can I not fit a model on this?' in the banner", async () => {
    // `01` §5.3's interaction requirement. The banner must say the blocking count and the
    // reason, not merely that something is wrong.
    render(ValidationReportView, { props });
    const banner = await screen.findByRole("status");
    expect(banner).toHaveAttribute("data-state", "blocked");
    expect(banner).toHaveTextContent("1 rule must pass before a model can be fitted");
    expect(banner).toHaveTextContent("There is no override");
  });

  it("orders the bands blocking → needs acknowledgement → everything else", async () => {
    // The fold ordering the spec prescribes. Asserted on document order, because "above
    // the fold" is a claim about sequence that a set of headings cannot make.
    render(ValidationReportView, { props });
    await screen.findByRole("status");

    const headings = screen
      .getAllByRole("heading", { level: 2 })
      // Trimmed: the template's line breaks are inside the element, so `textContent`
      // carries them and an anchored match would test the formatter, not the order.
      .map((h) => (h.textContent ?? "").trim());
    expect(headings[0]).toMatch(/^Blocking/);
    expect(headings[1]).toMatch(/^Needs acknowledgement/);
    expect(headings.slice(2).join(" ")).toMatch(/structural/);
  });

  it("shows measured beside threshold, because neither is actionable alone", async () => {
    render(ValidationReportView, { props });
    expect(await screen.findByText("violating_rows")).toBeInTheDocument();
    expect(screen.getByText("571")).toBeInTheDocument();
    expect(screen.getByText("max_inclusive (threshold)")).toBeInTheDocument();
    expect(screen.getByText("1.05")).toBeInTheDocument();
  });

  it("offers acknowledgement on an unacknowledged warning and nowhere else", async () => {
    render(ValidationReportView, { props });
    await screen.findByRole("status");
    // One button, on the warning — not on the failure, which `01` §1.3 forbids waving
    // through, and not on the pass.
    expect(screen.getAllByRole("button", { name: /acknowledge/i })).toHaveLength(1);
  });

  it("refuses to submit an acknowledgement without a justification", async () => {
    const user = userEvent.setup();
    render(ValidationReportView, { props });
    await screen.findByRole("status");
    await user.click(screen.getByRole("button", { name: /acknowledge…/i }));

    const dialog = await screen.findByRole("dialog");
    const confirm = within(dialog).getByRole("button", { name: "Acknowledge" });
    // FR-46: the justification is the audit record. The server refuses an empty one;
    // this only avoids the round trip.
    expect(confirm).toBeDisabled();

    await user.type(within(dialog).getByLabelText(/justification/i), "reviewed against 2023");
    expect(confirm).toBeEnabled();
  });

  it("posts the justification to the rule that was warned about", async () => {
    const user = userEvent.setup();
    render(ValidationReportView, { props });
    await screen.findByRole("status");
    await user.click(screen.getByRole("button", { name: /acknowledge…/i }));

    const dialog = await screen.findByRole("dialog");
    await user.type(within(dialog).getByLabelText(/justification/i), "seasonal, confirmed");
    await user.click(within(dialog).getByRole("button", { name: "Acknowledge" }));

    await waitFor(() => {
      const posted = vi.mocked(fetch).mock.calls.find(
        ([, init]) => (init as RequestInit | undefined)?.method === "POST",
      );
      expect(posted).toBeDefined();
      const [url, init] = posted as [string | URL, RequestInit];
      // The *warned* rule, not the failing one — a dialog that posted the wrong rule id
      // would acknowledge something nobody read.
      expect(String(url)).toContain(`/results/${SEVERITY_RULE}/acknowledge`);
      expect(JSON.parse(String(init.body))).toEqual({ justification: "seasonal, confirmed" });
    });
  });

  it("shows the platform's refusal rather than a generic failure", async () => {
    const user = userEvent.setup();
    render(ValidationReportView, { props });
    await screen.findByRole("status");
    await user.click(screen.getByRole("button", { name: /acknowledge…/i }));

    // An analyst gets `ACKNOWLEDGE_FORBIDDEN_ROLE`, which means "find an actuary" — a
    // different action from "ask for a grant", and the reason the platform owns a code
    // for it rather than returning a generic denial.
    vi.mocked(fetch).mockImplementationOnce(
      async () =>
        new Response(
          JSON.stringify({
            title: "Acknowledging a validation warning requires the Pricing Actuary role",
            status: 403,
            code: "ACKNOWLEDGE_FORBIDDEN_ROLE",
            detail: "FR-46 places this judgement with an actuary.",
            errors: [],
          }),
          { status: 403, headers: { "Content-Type": "application/json" } },
        ),
    );

    const dialog = await screen.findByRole("dialog");
    await user.type(within(dialog).getByLabelText(/justification/i), "looks fine");
    await user.click(within(dialog).getByRole("button", { name: "Acknowledge" }));

    expect(await within(dialog).findByRole("alert")).toHaveTextContent(
      /requires the Pricing Actuary role/i,
    );
  });
});
