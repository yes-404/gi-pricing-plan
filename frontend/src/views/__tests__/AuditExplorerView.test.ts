import { render, screen, waitFor } from "@testing-library/vue";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { AuditPage, ChainVerification } from "@/api/audit";

import AuditExplorerView from "../AuditExplorerView.vue";

const WORKSPACE = "01a0048c-766b-73cc-ac8b-af35d55fce8b";

const PAGE: AuditPage = {
  items: [
    {
      id: "01a0048c-da2f-7513-9de7-0a5e5a9e58cc",
      workspace_id: WORKSPACE,
      sequence: 2,
      at: "2026-09-13T10:11:00.482Z",
      actor: { kind: "user", id: "01a0048c-9f31-70b2-8c4d-6e5b1a2f7d90", display: "a.actuary" },
      source: "api",
      action: "model.approved",
      entity_ref: "model:motor-freq@2",
      justification: "within the envelope",
      before: { status: "review" },
      after: { status: "approved" },
      prev_event_hash: `sha256:${"a".repeat(64)}`,
      event_hash: `sha256:${"b".repeat(64)}`,
    },
  ],
  next_cursor: "cursor-2",
  total_estimate: 1500,
};

const INTACT: ChainVerification = {
  workspace_id: WORKSPACE,
  whole_chain: true,
  first_sequence: 1,
  last_sequence: 2,
  events_checked: 2,
  intact: true,
};

const ROUTER_LINK = { RouterLink: { props: ["to"], template: '<a :href="to"><slot /></a>' } };

type Reply = { status?: number; body: unknown; type?: string };
let replies: Reply[];

function urls(): URL[] {
  return vi.mocked(fetch).mock.calls.map(([url]) => new URL(String(url)));
}

beforeEach(() => {
  replies = [];
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => {
      const reply = replies.shift() ?? { body: PAGE };
      return new Response(
        typeof reply.body === "string" ? reply.body : JSON.stringify(reply.body),
        {
          status: reply.status ?? 200,
          headers: { "Content-Type": reply.type ?? "application/json" },
        },
      );
    }),
  );
  URL.createObjectURL = vi.fn(() => "blob:audit");
  URL.revokeObjectURL = vi.fn();
});
afterEach(() => vi.unstubAllGlobals());

async function view(): Promise<void> {
  render(AuditExplorerView, { global: { stubs: ROUTER_LINK } });
  await screen.findByRole("table");
}

describe("the audit explorer (FR-371, FR-372, FR-373)", () => {
  it("turns each filter into a query parameter", async () => {
    await view();
    await userEvent.type(screen.getByLabelText("Entity"), "model:motor-freq@2");
    await userEvent.type(screen.getByLabelText("Action"), "model.approved");
    await userEvent.type(screen.getByLabelText("Actor (user id)"), "u1");
    await userEvent.type(screen.getByLabelText("Justification text"), "envelope");
    await userEvent.click(screen.getByRole("button", { name: "Apply filters" }));
    await waitFor(() => expect(urls().length).toBe(2));
    expect(Object.fromEntries(urls()[1]!.searchParams)).toEqual({
      actor: "u1",
      entity: "model:motor-freq@2",
      action: "model.approved",
      q: "envelope",
    });
  });

  it("passes the cursor back verbatim and shows a capped total as 1,000+", async () => {
    await view();
    expect(screen.getByText(/1,000\+/)).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Load more" }));
    await waitFor(() => expect(urls().length).toBe(2));
    expect(urls()[1]!.searchParams.get("cursor")).toBe("cursor-2");
  });

  it("shows where the chain breaks, and what was checked when it holds", async () => {
    await view();
    replies.push({ body: INTACT });
    await userEvent.click(screen.getByRole("button", { name: "Verify whole chain" }));
    expect(await screen.findByText(/Chain intact: 2 events checked/)).toBeInTheDocument();
    expect(urls()[1]!.pathname).toBe("/api/v1/audit/verify");
    expect([...urls()[1]!.searchParams]).toEqual([]);

    replies.push({
      body: { ...INTACT, intact: false, broken_at_sequence: 2, reason: "content does not match stored hash" },
    });
    await userEvent.click(screen.getByRole("button", { name: "Verify whole chain" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Chain broken at sequence 2: content does not match stored hash",
    );
  });

  it("says tamper-evident against modification below the application, never tamper-proof", async () => {
    await view();
    const text = document.body.textContent ?? "";
    expect(text).toContain("tamper-evident against modification below the application");
    expect(text).not.toContain("tamper-proof");
  });

  it("exports with the filters the list was loaded with", async () => {
    await view();
    await userEvent.type(screen.getByLabelText("Action"), "model.approved");
    await userEvent.click(screen.getByRole("button", { name: "Apply filters" }));
    await waitFor(() => expect(urls().length).toBe(2));
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    replies.push({ body: '{"sequence":2}\n', type: "application/x-ndjson" });
    await userEvent.click(screen.getByRole("button", { name: "Export JSON Lines" }));
    await vi.waitFor(() => expect(click).toHaveBeenCalled());
    const exportUrl = urls()[2]!;
    expect(exportUrl.pathname).toBe("/api/v1/audit/export");
    expect(Object.fromEntries(exportUrl.searchParams)).toEqual({
      action: "model.approved",
      format: "json",
    });
    expect(click.mock.contexts[0]).toHaveProperty("download", "audit.jsonl");
    click.mockRestore();
  });

  it("sets the entity filter from a row's entity", async () => {
    await view();
    await userEvent.click(screen.getByRole("button", { name: "model:motor-freq@2" }));
    await waitFor(() => expect(urls().length).toBe(2));
    expect(urls()[1]!.searchParams.get("entity")).toBe("model:motor-freq@2");
  });

  it("links a row's entity to its history, percent-encoded", async () => {
    await view();
    expect(screen.getByRole("link", { name: "history" })).toHaveAttribute(
      "href",
      "/artifacts/model%3Amotor-freq%402/history",
    );
  });

  it("renders a refusal as the problem it is", async () => {
    replies.push({
      status: 403,
      body: { type: "about:blank", title: "Permission denied", status: 403, code: "PERMISSION_DENIED", detail: "audit:read is required" },
    });
    render(AuditExplorerView);
    expect(await screen.findByRole("alert")).toHaveTextContent("Permission denied");
  });
});
