import { render, screen, waitFor, within } from "@testing-library/vue";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import RuleSetView from "../RuleSetView.vue";

/** Shaped on the payload `GET /datasets/{slug}/rule-set` actually returns. */
function rule(over: Record<string, unknown> = {}) {
  return {
    id: "11111111-1111-4111-8111-111111111111",
    slug: "driv-age-range",
    version: 1,
    layer: "actuarial_sanity",
    check: "range",
    severity: "warn",
    target: { table: "policy_exposure", column: "driv_age" },
    params: { key_columns: ["policy_id"], min_inclusive: 18 },
    scope: {},
    tolerance: { max_fail_rate: 0.01 },
    message: "",
    rationale: "Under 18 cannot hold a policy.",
    status: "approved",
    ...over,
  };
}

function ruleSet(over: Record<string, unknown> = {}) {
  return {
    id: "22222222-2222-4222-8222-222222222222",
    slug: "fremtpl2",
    version: 3,
    dataset_id: "33333333-3333-4333-8333-333333333333",
    entries: [{ rule: rule(), enabled: true, severity_override: null }],
    reference_dataset_version_id: null,
    status: "approved",
    empty_layers: ["distributional", "referential", "structural"],
    ...over,
  };
}

let posted: string[] = [];
let putBodies: Record<string, unknown>[] = [];

function stub(body: unknown, status = 200, postStatus = 200, postBody?: unknown): void {
  posted = [];
  putBodies = [];
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: string | URL, init?: RequestInit) => {
      const url = String(input);
      if (init?.method === "PUT") {
        putBodies.push(JSON.parse(String(init.body)));
        return new Response(JSON.stringify(body), {
          status,
          headers: { "Content-Type": "application/json" },
        });
      }
      if (init?.method === "POST") {
        posted.push(url);
        return new Response(JSON.stringify(postBody ?? {}), {
          status: postStatus,
          headers: { "Content-Type": "application/json" },
        });
      }
      return new Response(JSON.stringify(body), {
        status,
        headers: { "Content-Type": "application/json" },
      });
    }),
  );
}

beforeEach(() => stub(ruleSet()));
afterEach(() => vi.unstubAllGlobals());

const props = { slug: "fremtpl2" };
const mounted = { global: { stubs: { RouterLink: { template: "<a><slot /></a>" } } } };

describe("the rule set view", () => {
  it("surfaces empty layers as FR-DATA-16's configuration warning", async () => {
    render(RuleSetView, { props, ...mounted });
    expect(await screen.findByText(/have no enabled rule/)).toBeInTheDocument();
    expect(screen.getByText(/distributional, referential, structural/)).toBeInTheDocument();
  });

  it("takes the empty layers from the server rather than deriving them", async () => {
    // The server counts *enabled* entries; a client re-deriving the rule would be a second
    // implementation of it, and the two would eventually disagree. Here the payload claims
    // `structural` is empty while carrying an enabled structural rule — an impossible state
    // the view must still report as the server sees it.
    stub(
      ruleSet({
        entries: [
          { rule: rule({ layer: "structural" }), enabled: true, severity_override: null },
        ],
      }),
    );
    render(RuleSetView, { props, ...mounted });
    expect(await screen.findByText(/distributional, referential, structural/)).toBeInTheDocument();
  });

  it("marks a disabled rule as disabled", async () => {
    // `empty_layers` counts enabled entries only, so a disabled rule rendered like any
    // other would contradict the banner directly above it.
    stub(
      ruleSet({
        entries: [{ rule: rule(), enabled: false, severity_override: null }],
        empty_layers: ["actuarial_sanity", "distributional", "referential", "structural"],
      }),
    );
    render(RuleSetView, { props, ...mounted });
    expect(await screen.findByText("disabled")).toBeInTheDocument();
    expect(screen.getAllByText(/No enabled rule in this layer/)).toHaveLength(4);
  });

  it("shows the thresholds the engine will use, from params and tolerance alike", async () => {
    render(RuleSetView, { props, ...mounted });
    const table = await screen.findByRole("table", { name: "actuarial_sanity" });
    expect(within(table).getByText(/min_inclusive=18/)).toBeInTheDocument();
    expect(within(table).getByText(/max_fail_rate=0.01/)).toBeInTheDocument();
    // `key_columns` targets the rule, it does not configure a threshold.
    expect(within(table).queryByText(/key_columns/)).not.toBeInTheDocument();
  });

  it("shows a severity override as the effective severity, and says it is overridden", async () => {
    stub(ruleSet({ entries: [{ rule: rule(), enabled: true, severity_override: "fail" }] }));
    render(RuleSetView, { props, ...mounted });
    const table = await screen.findByRole("table", { name: "actuarial_sanity" });
    expect(within(table).getByText("fail")).toBeInTheDocument();
    expect(within(table).getByText("overridden")).toBeInTheDocument();
  });

  it("reads a refusal to self-approve as separation of duties, not missing access", async () => {
    stub(ruleSet({ entries: [{ rule: rule({ status: "review" }), enabled: true, severity_override: null }] }),
      200, 409,
      { title: "Conflict", status: 409, code: "SUBMITTER_CANNOT_APPROVE", errors: [] });
    render(RuleSetView, { props, ...mounted });
    await userEvent.click(await screen.findByRole("button", { name: "Approve" }));
    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent(/Someone else must review it/);
    // The reader must not be sent looking for a grant they already hold.
    expect(alert).not.toHaveTextContent(/permission|access|forbidden/i);
  });

  it("offers submit on a draft and approve on a rule in review, never both", async () => {
    stub(
      ruleSet({
        entries: [
          { rule: rule({ status: "draft" }), enabled: true, severity_override: null },
          {
            rule: rule({ id: "44444444-4444-4444-8444-444444444444", status: "review" }),
            enabled: true,
            severity_override: null,
          },
        ],
      }),
    );
    render(RuleSetView, { props, ...mounted });
    expect(await screen.findByRole("button", { name: "Submit" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Approve" })).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Submit" }));
    await waitFor(() => expect(posted.some((u) => u.endsWith("/submit"))).toBe(true));
  });

  it("carries every other entry through when one is disabled", async () => {
    // A replace is the whole set (FR-DATA-22). Rebuilding the body from ids alone would
    // silently re-enable every other disabled entry and drop every other override — the
    // edit would do something nobody asked for and nothing would say so.
    stub(
      ruleSet({
        entries: [
          { rule: rule(), enabled: true, severity_override: "fail" },
          {
            rule: rule({ id: "44444444-4444-4444-8444-444444444444", layer: "structural" }),
            enabled: false,
            severity_override: null,
          },
        ],
      }),
    );
    render(RuleSetView, { props, ...mounted });
    const table = await screen.findByRole("table", { name: "actuarial_sanity" });
    await userEvent.click(within(table).getByRole("button", { name: "Disable" }));
    await waitFor(() => expect(putBodies).toHaveLength(1));
    expect(putBodies[0]!.rules).toEqual([
      { rule_id: rule().id, enabled: false, severity_override: "fail" },
      {
        rule_id: "44444444-4444-4444-8444-444444444444",
        enabled: false,
        severity_override: null,
      },
    ]);
  });

  it("offers to raise a warn to fail, and never to lower a fail", async () => {
    // `01` §4.3: raising tightens a shipped rule and needs no review. Lowering is a
    // decision that a failure is acceptable, and belongs in the rule's own review.
    stub(
      ruleSet({
        entries: [
          { rule: rule(), enabled: true, severity_override: null },
          {
            rule: rule({ id: "44444444-4444-4444-8444-444444444444", severity: "fail",
              layer: "structural" }),
            enabled: true,
            severity_override: null,
          },
        ],
      }),
    );
    render(RuleSetView, { props, ...mounted });
    const lenient = await screen.findByRole("table", { name: "actuarial_sanity" });
    const strict = screen.getByRole("table", { name: "structural" });
    expect(within(lenient).getByRole("button", { name: "Raise to fail" })).toBeInTheDocument();
    expect(within(strict).queryByRole("button", { name: /Raise|Clear/ })).toBeNull();

    await userEvent.click(within(lenient).getByRole("button", { name: "Raise to fail" }));
    await waitFor(() => expect(putBodies).toHaveLength(1));
    expect((putBodies[0]!.rules as { severity_override: string }[])[0]!.severity_override)
      .toBe("fail");
  });

  it("explains a refused downgrade as the rule's own review, not a failed request", async () => {
    stub(ruleSet(), 200);
    render(RuleSetView, { props, ...mounted });
    await screen.findByRole("table", { name: "actuarial_sanity" });
    // The server refuses; the screen must say what to do instead.
    stub(
      { title: "Conflict", status: 409, code: "RULE_SEVERITY_DOWNGRADE_FORBIDDEN", errors: [] },
      409,
    );
    await userEvent.click(screen.getByRole("button", { name: "Raise to fail" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(/may only raise severity/);
  });

  it("treats a dataset with no rule set as a state, not a failure", async () => {
    stub(
      {
        title: "This dataset has no rule set",
        status: 404,
        code: "NOT_FOUND",
        detail: "Dataset 'fremtpl2' has no Validation Rule Set. One must be defined "
          + "before the version can be validated (FR-DATA-16).",
        errors: [],
      },
      404,
    );
    render(RuleSetView, { props, ...mounted });
    expect(await screen.findByText(/One must be defined before/)).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
});
