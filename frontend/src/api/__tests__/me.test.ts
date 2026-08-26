import { afterEach, describe, expect, it, vi } from "vitest";

import { listWorkspaces, switchWorkspace } from "../me";
import { isProblem, ProblemError } from "../problem";

// UUID fixtures come from the repo's own tests (`DatasetListView.test.ts:206`), and the
// slug is the derived shape the platform itself produces (`workspaces.py:37-41`) — never
// invented literals.
const FIRST = "01a0048c-1111-7000-8000-222233334444";
const SECOND = "01a0048c-2222-7000-8000-333344445555";
const SLUG_FIRST = `ws-${FIRST.replaceAll("-", "")}`;

function respond(status: number, body: unknown): void {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () =>
      new Response(body === undefined ? null : JSON.stringify(body), {
        status,
        headers: { "Content-Type": "application/json" },
      }),
    ),
  );
}

afterEach(() => vi.unstubAllGlobals());

describe("the workspace client", () => {
  it("lists the memberships without a selection", async () => {
    respond(200, [
      { workspace_id: FIRST, slug: SLUG_FIRST, name: "Alpha" },
      { workspace_id: SECOND, slug: `ws-${SECOND.replaceAll("-", "")}`, name: "Beta" },
    ]);
    expect(await listWorkspaces()).toHaveLength(2);
  });

  it("posts the switch and returns the entered workspace", async () => {
    const entered = { workspace_id: SECOND, slug: `ws-${SECOND.replaceAll("-", "")}`, name: "Beta" };
    respond(200, entered);
    await expect(switchWorkspace(entered.workspace_id)).resolves.toEqual(entered);
    const [, init] = vi.mocked(fetch).mock.calls[0]!;
    expect(JSON.parse(String(init?.body))).toEqual({ workspace_id: entered.workspace_id });
  });

  it("surfaces a platform refusal as a ProblemError", async () => {
    respond(403, {
      type: "about:blank",
      title: "Forbidden",
      status: 403,
      code: "WORKSPACE_SCOPE_DENIED",
      detail: "The Workspace-Id header names a workspace this principal is not a member of.",
      errors: [],
    });
    await expect(listWorkspaces()).rejects.toSatisfy(
      (e: unknown) => e instanceof ProblemError && isProblem(e) && e.code === "WORKSPACE_SCOPE_DENIED",
    );
  });
});
