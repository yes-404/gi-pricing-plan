import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { request } from "../../api/client";
import { useWorkspaceStore } from "../workspace";

// UUID fixtures come from the repo's own tests (`DatasetListView.test.ts:206`), the slug
// is the derived shape the platform produces (`workspaces.py:37-41`) — never invented.
const FIRST = "01a0048c-1111-7000-8000-222233334444";
const SECOND = "01a0048c-2222-7000-8000-333344445555";
const OTHER = "01a0048c-766b-73cc-ac8b-af35d55fce8b";
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
});

describe("the workspace store", () => {
  it("restores a remembered selection on load and skips it when stale", async () => {
    // The remembered id is a membership → it becomes current, and the header follows.
    sessionStorage.setItem("gi.workspaceId", SECOND);
    respond(200, [membership(FIRST, "Alpha"), membership(SECOND, "Beta")]);
    const store = useWorkspaceStore();
    await store.load();
    expect(store.current?.workspace_id).toBe(SECOND);

    respond(200, {});
    await request("/anything");
    const headers = new Headers(vi.mocked(fetch).mock.calls[0]?.[1]?.headers);
    expect(headers.get("Workspace-Id")).toBe(SECOND);

    // A stale remembered id (membership revoked) is never sent: with one membership it
    // falls back to that member; with several it falls back to null — the platform
    // refuses until the user picks (FR-397), never someone else's data.
    sessionStorage.setItem("gi.workspaceId", OTHER);
    respond(200, [membership(FIRST, "Alpha")]);
    await store.load();
    expect(store.current?.workspace_id).toBe(FIRST);

    respond(200, [membership(FIRST, "Alpha"), membership(SECOND, "Beta")]);
    await store.load();
    expect(store.current).toBeNull();

    respond(200, {});
    await request("/anything");
    expect(
      new Headers(vi.mocked(fetch).mock.calls[0]?.[1]?.headers).has("Workspace-Id"),
    ).toBe(false);
  });

  it("defaults a single membership to the only member", async () => {
    respond(200, [membership(FIRST, "Alpha")]);
    const store = useWorkspaceStore();
    await store.load();
    expect(store.current?.workspace_id).toBe(FIRST);
    expect(store.needsSelection).toBe(false);
  });

  it("select() posts the switch, remembers it, and reloads", async () => {
    vi.spyOn(window.location, "reload").mockImplementation(() => undefined);
    const entered = membership(SECOND, "Beta");
    respond(200, entered);
    const store = useWorkspaceStore();
    await store.select(SECOND);

    const [url, init] = vi.mocked(fetch).mock.calls[0]!;
    expect(String(url)).toMatch(/\/api\/v1\/me\/workspace$/);
    expect(init?.method).toBe("POST");
    expect(JSON.parse(String(init?.body))).toEqual({ workspace_id: SECOND });

    expect(store.current).toEqual(entered);
    expect(sessionStorage.getItem("gi.workspaceId")).toBe(SECOND);
    expect(vi.isMockFunction(window.location.reload)).toBe(true);
  });
});
