import { render, screen, waitFor, within } from "@testing-library/vue";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { SystemStatus } from "@/api/systemStatus";
import { routes } from "@/router";

import SystemStatusView from "../SystemStatusView.vue";

// Every body is typed from the generated client, never restated by hand (CLAUDE.md §4).
const UP: SystemStatus = {
  status: "up",
  components: [
    { name: "blobs", status: "up", detail: null },
    { name: "database", status: "up", detail: null },
    { name: "redis", status: "down", detail: "unreachable: ConnectionError" },
  ],
  schema_version: "e5b2a7d94c13",
  queues: [{ kind: "dataset.ingest", status: "queued", depth: 2 }],
  blob_store: { objects: 41, bytes: 1048576 },
  caches: [{ name: "bundle_slot", hits: 120, misses: 3 }],
};

function serve(status: number, body: unknown): void {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () =>
      new Response(JSON.stringify(body), {
        status,
        headers: { "Content-Type": "application/json" },
      }),
    ),
  );
}

async function shown(body: SystemStatus): Promise<void> {
  serve(200, body);
  render(SystemStatusView);
  await screen.findByRole("heading", { name: /system status/i });
  await waitFor(() => expect(screen.queryByText(/loading/i)).toBeNull());
}

afterEach(() => vi.unstubAllGlobals());

describe("SystemStatusView, components (07 §4.6, FR-444)", () => {
  it("labels a down component in words as well as by colour", async () => {
    await shown(UP);
    const row = screen.getByText("redis").closest("li")!;
    expect(within(row).getByText("down")).toBeTruthy();
    expect(within(row).getByText(/unreachable: ConnectionError/)).toBeTruthy();
    const ok = screen.getByText("database").closest("li")!;
    expect(within(ok).getByText("up")).toBeTruthy();
  });

  it("reports the whole as up while a non-gating component is down", async () => {
    await shown(UP);
    expect(screen.getByTestId("overall-status").textContent).toMatch(/up/);
  });

  it("shows 'down' in the overall badge when the route's status is down, in words and in red", async () => {
    await shown({
      ...UP,
      status: "down",
      components: [
        { name: "blobs", status: "up", detail: null },
        { name: "database", status: "down", detail: "could not be read: SQLAlchemyError" },
        { name: "redis", status: "up", detail: null },
      ],
    });
    const overall = screen.getByTestId("overall-status");
    expect(overall.textContent).toBe("down");
    expect(overall.className).toMatch(/red/);
    expect(overall.className).not.toMatch(/green/);
  });
});

describe("SystemStatusView, caches (07 §4.6)", () => {
  it("derives a rate from hits and misses", async () => {
    await shown(UP);
    const row = screen.getByText("bundle_slot").closest("tr")!;
    expect(within(row).getByText(/97\.6\s?%/)).toBeTruthy();
  });

  it("shows 'no reads yet' for a cache with no reads, never 0 %", async () => {
    await shown({ ...UP, caches: [{ name: "bundle_slot", hits: 0, misses: 0 }] });
    const row = screen.getByText("bundle_slot").closest("tr")!;
    expect(within(row).getByText(/no reads yet/i)).toBeTruthy();
    expect(row.textContent).not.toMatch(/0\s?%/);
  });
});

describe("SystemStatusView, null means 'could not be read' (decision, #1505 comment 7070124577)", () => {
  const DOWN: SystemStatus = {
    ...UP,
    status: "down",
    components: [{ name: "database", status: "down", detail: "OperationalError" }],
  };

  it("shows a null schema_version in words, never blank", async () => {
    await shown({ ...DOWN, schema_version: null });
    expect(screen.getByTestId("schema-version").textContent).toMatch(/could not be read/i);
  });

  it("shows null queues in words, never an empty list", async () => {
    await shown({ ...DOWN, queues: null });
    expect(screen.getByTestId("queues").textContent).toMatch(/could not be read/i);
    expect(screen.queryByText(/nothing queued/i)).toBeNull();
  });

  it("shows a null blob_store in words, never as zero", async () => {
    await shown({ ...DOWN, blob_store: null });
    const text = screen.getByTestId("blob-store").textContent ?? "";
    expect(text).toMatch(/could not be read/i);
    expect(text).not.toMatch(/\b0\b/);
  });

  it("keeps the meanings of an empty list and of zeros when the read succeeded", async () => {
    await shown({ ...UP, queues: [], blob_store: { objects: 0, bytes: 0 } });
    expect(screen.getByTestId("queues").textContent).toMatch(/nothing queued/i);
    expect(screen.getByTestId("queues").textContent).not.toMatch(/could not be read/i);
    expect(screen.getByTestId("blob-store").textContent).toMatch(/0 objects/);
    expect(screen.getByTestId("blob-store").textContent).not.toMatch(/could not be read/i);
  });
});

describe("SystemStatusView, who may open it (decision 7060618416, answer 1)", () => {
  it("the route asks for sign-in only, and the view renders the body it is given", async () => {
    // Every built-in role holds settings:read, so any role can open the view; the platform
    // refuses only a caller with no role, and that arrives as a 403, shown as an alert (the
    // next test). The frontend holds no role, so what it can hold is that the route carries
    // no gate beyond sign-in. Who is refused is the backend's test, not this one's.
    const route = routes.find((r) => r.path === "/admin/status");
    expect(route?.meta).toEqual({ requiresAuth: true });
    await shown(UP);
    expect(screen.getByTestId("schema-version").textContent).toContain("e5b2a7d94c13");
  });

  it("a 403 from the platform is shown as an alert, not an empty page", async () => {
    serve(403, {
      type: "about:blank", title: "Forbidden", status: 403, code: "FORBIDDEN", errors: [],
    });
    render(SystemStatusView);
    expect(await screen.findByRole("alert")).toBeTruthy();
  });
});
