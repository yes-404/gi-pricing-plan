import { render, screen } from "@testing-library/vue";
import { fireEvent } from "@testing-library/vue";
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useWorkspaceStore } from "@/stores/workspace";

import WorkspaceSelector from "../WorkspaceSelector.vue";

// UUID fixtures come from the repo's own tests (`DatasetListView.test.ts:206`), the slug
// is the derived shape the platform produces (`workspaces.py:37-41`) — never invented.
const FIRST = "01a0048c-1111-7000-8000-222233334444";
const SECOND = "01a0048c-2222-7000-8000-333344445555";
const membership = (workspace_id: string, name: string) => ({
  workspace_id,
  slug: `ws-${workspace_id.replaceAll("-", "")}`,
  name,
});

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

beforeEach(() => {
  setActivePinia(createPinia());
  sessionStorage.clear();
  vi.restoreAllMocks();
});

describe("the workspace selector", () => {
  it("loads the memberships on mount and shows the current workspace name", async () => {
    sessionStorage.setItem("gi.workspaceId", FIRST);
    respond(200, [membership(FIRST, "Alpha"), membership(SECOND, "Beta")]);
    render(WorkspaceSelector);

    const selector = await screen.findByTestId("workspace-selector");
    const names = Array.from(selector.querySelectorAll("option")).map(
      (option) => option.textContent,
    );
    expect(names).toEqual(["Alpha", "Beta"]);
    // The current workspace is named alongside the control (FR-395's name).
    expect(selector.querySelector("span")?.textContent).toBe("Alpha");
    expect(selector.querySelector("select")?.value).toBe(FIRST);
  });

  it("renders nothing when the list is empty", async () => {
    // A Service Account has no memberships (`me.py:114-117`) — an empty list is normal,
    // and the shell shows no dangling control for it.
    respond(200, []);
    render(WorkspaceSelector);

    expect(screen.queryByTestId("workspace-selector")).toBeNull();
  });

  it("calls store.select on change", async () => {
    vi.spyOn(window.location, "reload").mockImplementation(() => undefined);
    respond(200, [membership(FIRST, "Alpha"), membership(SECOND, "Beta")]);
    render(WorkspaceSelector);
    const selector = await screen.findByTestId("workspace-selector");

    // The switch is a second exchange with its own response — the stub serves one body
    // per `respond` call, and the POST must resolve to the entered workspace.
    respond(200, membership(SECOND, "Beta"));
    fireEvent.update(selector.querySelector("select")!, SECOND);

    // `select()` is async: the switch response resolves into `current` after the POST.
    await vi.waitFor(() => expect(useWorkspaceStore().current?.workspace_id).toBe(SECOND));
    // The second `respond` replaced the fetch mock, so the switch is its first call.
    expect(vi.mocked(fetch).mock.calls).toHaveLength(1);
    const [url, init] = vi.mocked(fetch).mock.calls[0]!;
    expect(String(url)).toMatch(/\/api\/v1\/me\/workspace$/);
    expect(init?.method).toBe("POST");
    expect(JSON.parse(String(init?.body))).toEqual({ workspace_id: SECOND });
  });
});
