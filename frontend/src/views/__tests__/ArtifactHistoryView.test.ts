import { render, screen } from "@testing-library/vue";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { ArtifactHistory } from "@/api/audit";

import ArtifactHistoryView from "../ArtifactHistoryView.vue";

const ROUTER_LINK = { RouterLink: { props: ["to"], template: '<a :href="to"><slot /></a>' } };
const ACTOR = { kind: "user", id: "01a0048c-9f31-70b2-8c4d-6e5b1a2f7d90", display: "a.actuary" } as const;

const HISTORY: ArtifactHistory = {
  ref: "model:motor-freq@2",
  events: [
    {
      sequence: 4,
      at: "2026-09-12T09:00:00Z",
      actor: ACTOR,
      source: "api",
      action: "model.submitted",
      transition: { from: "fitted", to: "review" },
      justification: "ready for review",
      diff: [{ path: "status", before: "fitted", after: "review" }],
    },
    {
      sequence: 9,
      at: "2026-09-13T10:11:00Z",
      actor: { ...ACTOR, display: "an.approver" },
      source: "ui",
      action: "model.approved",
      transition: { from: "review", to: "approved" },
      justification: "within the envelope",
      diff: [
        { path: "approvers_recorded", before: 1, after: 2 },
        { path: "status", before: "review", after: "approved" },
      ],
    },
  ],
};

function reply(status: number, body: unknown): void {
  vi.stubGlobal(
    "fetch",
    vi.fn(
      async () =>
        new Response(JSON.stringify(body), {
          status,
          headers: { "Content-Type": "application/json" },
        }),
    ),
  );
}

function problem(status: number, code: string, title: string) {
  return { type: "about:blank", title, status, code, detail: `${title}.` };
}

function show(artifactRef = "model:motor-freq@2"): void {
  render(ArtifactHistoryView, { props: { artifactRef }, global: { stubs: ROUTER_LINK } });
}

beforeEach(() => reply(200, HISTORY));
afterEach(() => vi.unstubAllGlobals());

describe("the artifact history view (FR-383)", () => {
  it("renders each event's transition, actor, time, justification and diff", async () => {
    show();
    expect(await screen.findByText(/fitted → review/)).toBeInTheDocument();
    expect(screen.getByText(/review → approved/)).toBeInTheDocument();
    expect(screen.getByText(/an\.approver/)).toBeInTheDocument();
    expect(screen.getByText("within the envelope")).toBeInTheDocument();
    expect(screen.getByText("approvers_recorded")).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledOnce();
    expect(String(vi.mocked(fetch).mock.calls[0]![0])).toContain(
      "/api/v1/artifacts/model%3Amotor-freq%402/history",
    );
  });

  it("shows a pre-rename return under its stored name, with its current name beside it", async () => {
    reply(200, {
      ...HISTORY,
      events: [
        { ...HISTORY.events[0]!, action: "model.fitted", current_action: "model.returned" },
        HISTORY.events[1]!,
      ],
    });
    show();
    expect(await screen.findByText("model.fitted")).toBeInTheDocument();
    expect(screen.getAllByText(/stored name; now written model\.returned/)).toHaveLength(1);
    expect(screen.getByText("model.approved")).toBeInTheDocument();
  });

  it("moves to the adjacent versions", async () => {
    show("model:motor-freq@2");
    await screen.findByText(/fitted → review/);
    expect(screen.getByRole("link", { name: "Previous version" })).toHaveAttribute(
      "href",
      "/artifacts/model%3Amotor-freq%401/history",
    );
    expect(screen.getByRole("link", { name: "Next version" })).toHaveAttribute(
      "href",
      "/artifacts/model%3Amotor-freq%403/history",
    );
  });

  it("offers no previous version before version 2", async () => {
    show("model:motor-freq@1");
    await screen.findByText(/fitted → review/);
    expect(screen.queryByRole("link", { name: "Previous version" })).toBeNull();
  });

  it("says there is no recorded history on a 404", async () => {
    reply(404, problem(404, "NOT_FOUND", "No recorded history"));
    show();
    expect(await screen.findByRole("alert")).toHaveTextContent("No recorded history");
  });

  it("says it is not an artifact on a 422", async () => {
    reply(422, problem(422, "VALIDATION_FAILED", "Not an artifact reference"));
    show("blob:gc@1");
    expect(await screen.findByRole("alert")).toHaveTextContent("This reference is not an artifact.");
  });

  it("shows a 403 as the problem it is", async () => {
    reply(403, problem(403, "PERMISSION_DENIED", "Permission denied"));
    show();
    expect(await screen.findByRole("alert")).toHaveTextContent("Permission denied");
  });
});
