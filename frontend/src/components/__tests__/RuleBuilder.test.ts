import { render, screen } from "@testing-library/vue";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import RuleBuilder from "../RuleBuilder.vue";

const VERSIONS = { items: [{ id: "aaaa", version: 3 }], next_cursor: null };
const RULE = { id: "rule-1", slug: "driv-age", status: "draft" };

let calls: string[] = [];

function stub(jobStatuses: string[] = ["succeeded"]): void {
  calls = [];
  let poll = 0;
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: string | URL, init?: RequestInit) => {
      const url = String(input);
      const method = init?.method ?? "GET";
      calls.push(`${method} ${url.replace(/^.*\/api\/v1/, "")}`);
      const json = (body: unknown, status = 200) =>
        new Response(JSON.stringify(body), {
          status,
          headers: { "Content-Type": "application/json" },
        });

      if (url.includes("/versions")) return json(VERSIONS);
      if (url.endsWith("/validation-rules")) return json(RULE, 201);
      if (url.includes("/dry-run")) return json({ id: "job-1", status: "queued" }, 202);
      if (url.includes("/jobs/")) {
        const status = jobStatuses[Math.min(poll, jobStatuses.length - 1)];
        poll += 1;
        return json({ id: "job-1", status });
      }
      if (url.includes("/submit")) return json({ ...RULE, status: "review" });
      return json({ title: "?", status: 404, code: "NOT_FOUND", errors: [] }, 404);
    }),
  );
}

beforeEach(() => stub());
afterEach(() => vi.unstubAllGlobals());

async function fill(): Promise<void> {
  await userEvent.type(await screen.findByLabelText("Slug"), "driv-age");
  await userEvent.type(screen.getByLabelText("Column"), "driv_age");
  await userEvent.clear(screen.getByLabelText("Parameters (JSON)"));
  await userEvent.type(screen.getByLabelText("Parameters (JSON)"), '{{"min_inclusive": 18}');
}

describe("the rule builder", () => {
  it("walks FR-DATA-21's chain in order: author, dry-run, submit", async () => {
    render(RuleBuilder, { props: { slug: "fremtpl2" } });
    await fill();
    await userEvent.click(screen.getByRole("button", { name: /Author, dry-run and submit/ }));

    expect(await screen.findByText(/Submitted for approval/)).toBeInTheDocument();
    // Order matters: submission is refused without a dry run, because an approver reading
    // a rule's JSON cannot tell whether it selects three rows or three million.
    expect(calls.filter((c) => c.startsWith("POST"))).toEqual([
      "POST /validation-rules",
      "POST /validation-rules/rule-1/dry-run",
      "POST /validation-rules/rule-1/submit",
    ]);
  });

  it("does not submit a rule whose dry run failed", async () => {
    stub(["failed"]);
    render(RuleBuilder, { props: { slug: "fremtpl2" } });
    await fill();
    await userEvent.click(screen.getByRole("button", { name: /Author, dry-run and submit/ }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/dry run failed/);
    expect(calls.some((c) => c.includes("/submit"))).toBe(false);
  });

  it("waits for a running job rather than reading its first state", async () => {
    stub(["queued", "running", "succeeded"]);
    render(RuleBuilder, { props: { slug: "fremtpl2" } });
    await fill();
    await userEvent.click(screen.getByRole("button", { name: /Author, dry-run and submit/ }));

    expect(await screen.findByText(/Submitted for approval/, {}, { timeout: 5000 }))
      .toBeInTheDocument();
    expect(calls.filter((c) => c.includes("/jobs/"))).toHaveLength(3);
  }, 10000);

  it("rejects unparseable parameters here rather than posting them", async () => {
    // A 422 from the server would name a field the user cannot see; the fix is in this box.
    render(RuleBuilder, { props: { slug: "fremtpl2" } });
    await userEvent.type(await screen.findByLabelText("Slug"), "driv-age");
    await userEvent.clear(screen.getByLabelText("Parameters (JSON)"));
    await userEvent.type(screen.getByLabelText("Parameters (JSON)"), "min=18");
    await userEvent.click(screen.getByRole("button", { name: /Author, dry-run and submit/ }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/valid JSON/);
    expect(calls.some((c) => c.startsWith("POST"))).toBe(false);
  });

  it("says why it cannot submit when the dataset has no version to run against", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        new Response(JSON.stringify({ items: [], next_cursor: null }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );
    render(RuleBuilder, { props: { slug: "fremtpl2" } });
    expect(await screen.findByText(/this dataset has none yet/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Author, dry-run and submit/ })).toBeDisabled();
  });
});
