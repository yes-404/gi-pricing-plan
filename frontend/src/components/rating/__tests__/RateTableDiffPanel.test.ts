import userEvent from "@testing-library/user-event";
import { render, screen, waitFor, within } from "@testing-library/vue";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ProblemError } from "@/api/problem";

import RateTableDiffPanel from "../RateTableDiffPanel.vue";

const getDiffCells = vi.fn();
const waitForJob = vi.fn();

vi.mock("@/api/rateTables", () => ({
  getDiffCells: (...args: unknown[]) => getDiffCells(...args),
  isJob: (answer: object) => !("items" in answer),
}));
vi.mock("@/api/jobs", () => ({
  waitForJob: (...args: unknown[]) => waitForJob(...args),
  TERMINAL: ["succeeded", "failed", "cancelled"],
}));

const cell = (area: string, rel: string | null, weight: string | null) => ({
  key: { area },
  change: "changed",
  baseline_value: "1.0000",
  current_value: "1.0500",
  abs_change: "0.0500",
  rel_change_pct: rel,
  weight,
});
const PAGE_ONE = {
  items: [cell("A", "5.0000", "120.5"), cell("B", "-0.4", "0")],
  next_cursor: "C1",
  total_estimate: 3,
};
const PAGE_TWO = { items: [cell("C", "20", null)], next_cursor: null, total_estimate: 3 };
const props = { tableRef: "area@3", pollIntervalMs: 0, pollAttempts: 2 };

beforeEach(() => {
  vi.resetAllMocks();
  getDiffCells.mockImplementation(async (_ref: string, query: { cursor?: string }) =>
    query.cursor === "C1" ? PAGE_TWO : PAGE_ONE,
  );
});

async function show(against: "previous" | "seed" = "previous"): Promise<void> {
  if (against === "seed") await userEvent.selectOptions(screen.getByLabelText("Compare against"), "seed");
  await userEvent.click(screen.getByRole("button", { name: "Show changes" }));
}

describe("RateTableDiffPanel (FR-231, FR-232)", () => {
  it("compares against the previous version by default, with no portfolio, and shows the changed cells", async () => {
    render(RateTableDiffPanel, { props });
    await show();
    expect(getDiffCells).toHaveBeenCalledWith("area@3", { against: "previous" });
    const rows = await screen.findAllByRole("row");
    expect(within(rows[1]!).getByRole("rowheader")).toHaveTextContent("A");
    expect(within(rows[1]!).getByText("+5.0000%")).toBeInTheDocument();
  });

  // FR-230: edits are diffed against the seed on request (the diff-vs-seed limb).
  it("compares against the seed on request", async () => {
    render(RateTableDiffPanel, { props });
    await show("seed");
    expect(getDiffCells).toHaveBeenCalledWith("area@3", { against: "seed" });
  });

  it("shows the exposure weight column only when a portfolio is named, and sends it", async () => {
    render(RateTableDiffPanel, { props });
    await show();
    await screen.findAllByRole("row");
    expect(screen.queryByRole("columnheader", { name: "Exposure weight" })).toBeNull();
    await userEvent.type(screen.getByLabelText("Portfolio Dataset Version"), "7a1c");
    await show();
    await waitFor(() =>
      expect(getDiffCells).toHaveBeenLastCalledWith("area@3", { against: "previous", portfolio: "7a1c" }),
    );
    expect(await screen.findByRole("columnheader", { name: "Exposure weight" })).toBeInTheDocument();
    expect(screen.getByText("120.5")).toBeInTheDocument();
  });

  it("writes the direction of each change as well as shading it", async () => {
    render(RateTableDiffPanel, { props });
    await show();
    const up = await screen.findByText("+5.0000%");
    const down = screen.getByText("-0.4%");
    expect(up.getAttribute("data-direction")).toBe("up");
    expect(down.getAttribute("data-direction")).toBe("down");
    expect(up.closest("td")!.className).toContain("bg-amber-");
    expect(down.closest("td")!.className).toContain("bg-sky-");
  });

  it("pages by the server cursor, forward and back, never reading ahead", async () => {
    render(RateTableDiffPanel, { props });
    await show();
    await screen.findAllByRole("row");
    expect(getDiffCells).toHaveBeenCalledTimes(1);
    await userEvent.click(screen.getByRole("button", { name: "Next page" }));
    expect(await screen.findByText("+20%")).toBeInTheDocument();
    expect(getDiffCells).toHaveBeenLastCalledWith("area@3", { against: "previous", cursor: "C1" });
    await userEvent.click(screen.getByRole("button", { name: "Previous page" }));
    expect(await screen.findByText("+5.0000%")).toBeInTheDocument();
  });

  it("polls the Job a 202 names, then reads the page it built", async () => {
    getDiffCells
      .mockResolvedValueOnce({ id: "j1", kind: "rate_table.diff_cells", status: "queued" })
      .mockResolvedValueOnce(PAGE_ONE);
    waitForJob.mockResolvedValue({ id: "j1", status: "succeeded" });
    render(RateTableDiffPanel, { props });
    await show();
    expect(await screen.findByText("+5.0000%")).toBeInTheDocument();
    expect(waitForJob).toHaveBeenCalledWith("j1", { attempts: 2, intervalMs: 0 });
    expect(getDiffCells).toHaveBeenCalledTimes(2);
  });

  it("says a Job that is still running when the wait ends is still running, not failed", async () => {
    getDiffCells.mockResolvedValueOnce({ id: "j1", kind: "rate_table.diff_cells", status: "queued" });
    waitForJob.mockResolvedValue({ id: "j1", status: "running" });
    render(RateTableDiffPanel, { props });
    await show();
    expect(await screen.findByText(/still running/i)).toBeInTheDocument();
    expect(screen.queryByRole("alert")).toBeNull();
  });

  it("shows a failed Job's own message", async () => {
    getDiffCells.mockResolvedValueOnce({ id: "j1", kind: "rate_table.diff_cells", status: "queued" });
    waitForJob.mockResolvedValue({ id: "j1", status: "failed", error: { message: "portfolio unreadable" } });
    render(RateTableDiffPanel, { props });
    await show();
    expect(await screen.findByRole("alert")).toHaveTextContent("portfolio unreadable");
  });

  it("shows the platform's refusal, such as a portfolio that is not validated", async () => {
    getDiffCells.mockRejectedValueOnce(
      new ProblemError({
        type: "about:blank",
        title: "Dataset version not validated",
        status: 422,
        code: "DATASET_VERSION_NOT_VALIDATED",
        detail: "The portfolio must be a validated Dataset Version.",
        errors: [],
      }),
    );
    render(RateTableDiffPanel, { props });
    await show();
    expect(await screen.findByRole("alert")).toHaveTextContent("The portfolio must be a validated Dataset Version.");
  });
});

// NFR-463 / WCAG 4.1.3 (FD-1959 F3): a status message is announced only if its live region is in
// the DOM before the message arrives. A region that mounts together with its text (v-if) is not.
const liveRegions = (root: HTMLElement): HTMLElement[] =>
  Array.from(root.querySelectorAll<HTMLElement>('[role="status"], [aria-live="polite"]'));

describe("RateTableDiffPanel: the status region is persistent (NFR-463, FD-1959 F3)", () => {
  it("holds the loading status in a live region that was in the DOM before Show changes", async () => {
    let release: (page: typeof PAGE_ONE) => void = () => undefined;
    getDiffCells.mockImplementationOnce(() => new Promise((resolve) => { release = resolve; }));
    const { container } = render(RateTableDiffPanel, { props });
    const before = liveRegions(container);
    await show();
    const holder = liveRegions(container).find((el) => /Loading/.test(el.textContent ?? ""));
    expect(holder).toBeDefined();
    expect(before).toContain(holder);
    release(PAGE_ONE);
    await screen.findAllByRole("row");
  });
});

describe("RateTableDiffPanel: the scrolling results are keyboard reachable (NFR-463, FD-1959 F6)", () => {
  it("makes the horizontally scrolling results region focusable", async () => {
    const { container } = render(RateTableDiffPanel, { props });
    await show();
    await screen.findAllByRole("row");
    const scroller = container.querySelector(".overflow-x-auto");
    expect(scroller).not.toBeNull();
    expect(scroller).toHaveAttribute("tabindex", "0");
  });
});
