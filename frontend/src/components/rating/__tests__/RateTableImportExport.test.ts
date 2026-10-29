import userEvent from "@testing-library/user-event";
import { render, screen } from "@testing-library/vue";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ProblemError } from "@/api/problem";

import RateTableImportExport from "../RateTableImportExport.vue";

const exportCsv = vi.fn();
const previewImport = vi.fn();
const confirmImport = vi.fn();

vi.mock("@/api/rateTables", () => ({
  exportCsv: (...args: unknown[]) => exportCsv(...args),
  previewImport: (...args: unknown[]) => previewImport(...args),
  confirmImport: (...args: unknown[]) => confirmImport(...args),
}));

const PREVIEW = {
  diff: { changed_cells: 2, max_abs_change_pct: "7.5", exposure_weighted_mean_change_pct: null },
  created_by_import: {
    applied_to: "rate_table:area@3",
    content_sha256: "ab".repeat(32),
    filename: "area.csv",
    round_trip: "passed",
  },
};
const props = { tableRef: "area@3" };
const csv = (): File => new File(["area,relativity\nA,1.05\n"], "area.csv", { type: "text/csv" });

beforeEach(() => {
  vi.resetAllMocks();
  URL.createObjectURL = vi.fn(() => "blob:csv");
  URL.revokeObjectURL = vi.fn();
});
afterEach(() => vi.restoreAllMocks());

async function pick(): Promise<void> {
  await userEvent.upload(screen.getByLabelText("CSV file"), csv());
}

describe("RateTableImportExport (FR-235)", () => {
  it("exports the version's CSV as a download named for the version", async () => {
    exportCsv.mockResolvedValue("area,relativity\nA,1.05\n");
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    render(RateTableImportExport, { props });
    await userEvent.click(screen.getByRole("button", { name: "Export CSV" }));
    await vi.waitFor(() => expect(click).toHaveBeenCalled());
    expect(exportCsv).toHaveBeenCalledWith("area@3");
    const blob = vi.mocked(URL.createObjectURL).mock.calls[0]![0] as Blob;
    expect(await blob.text()).toBe("area,relativity\nA,1.05\n");
    expect(click.mock.contexts[0]).toHaveProperty("download", "area@3.csv");
  });

  it("checks a chosen file first and shows the diff it would make, creating nothing", async () => {
    previewImport.mockResolvedValue(PREVIEW);
    render(RateTableImportExport, { props });
    await pick();
    await userEvent.click(screen.getByRole("button", { name: "Check file" }));
    expect(await screen.findByText("2 cells would change")).toBeInTheDocument();
    expect(screen.getByText(/Largest relative change: 7.5%/)).toBeInTheDocument();
    expect(screen.getByText(/area\.csv/)).toBeInTheDocument();
    expect(previewImport).toHaveBeenCalledWith("area@3", expect.objectContaining({ name: "area.csv" }));
    expect(confirmImport).not.toHaveBeenCalled();
  });

  it("creates the version only after the actuary confirms the same file", async () => {
    previewImport.mockResolvedValue(PREVIEW);
    confirmImport.mockResolvedValue({ slug: "area", version: 4 });
    const { emitted } = render(RateTableImportExport, { props });
    await pick();
    await userEvent.click(screen.getByRole("button", { name: "Check file" }));
    await userEvent.click(await screen.findByRole("button", { name: "Confirm and create version" }));
    expect(confirmImport).toHaveBeenCalledWith("area@3", expect.objectContaining({ name: "area.csv" }));
    expect(await screen.findByText("Created area@4")).toBeInTheDocument();
    expect(emitted().created).toEqual([[{ slug: "area", version: 4 }]]);
  });

  it("drops the preview when a different file is chosen, so a stale diff cannot be confirmed", async () => {
    previewImport.mockResolvedValue(PREVIEW);
    render(RateTableImportExport, { props });
    await pick();
    await userEvent.click(screen.getByRole("button", { name: "Check file" }));
    await screen.findByText("2 cells would change");
    await userEvent.upload(screen.getByLabelText("CSV file"), new File(["x"], "other.csv", { type: "text/csv" }));
    expect(screen.queryByText("2 cells would change")).toBeNull();
    expect(screen.queryByRole("button", { name: "Confirm and create version" })).toBeNull();
  });

  it("shows why the platform refused a file that fails the round trip", async () => {
    previewImport.mockRejectedValueOnce(
      new ProblemError({
        type: "about:blank",
        title: "Import refused",
        status: 422,
        code: "RATE_TABLE_IMPORT_REFUSED",
        detail: "The file's keys do not cover the table's domain.",
        errors: [],
      }),
    );
    render(RateTableImportExport, { props });
    await pick();
    await userEvent.click(screen.getByRole("button", { name: "Check file" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("do not cover the table's domain");
  });

  it("will not check until a file is chosen", () => {
    render(RateTableImportExport, { props });
    expect(screen.getByRole("button", { name: "Check file" })).toBeDisabled();
  });
});

// NFR-463 / WCAG 4.1.3 (FD-1959 F3): a status message is announced only if its live region is in
// the DOM before the message arrives. A region that mounts together with its text (v-if) is not.
const liveRegions = (root: HTMLElement): HTMLElement[] =>
  Array.from(root.querySelectorAll<HTMLElement>('[role="status"], [aria-live="polite"]'));

describe("RateTableImportExport: the status region is persistent (NFR-463, FD-1959 F3)", () => {
  it("holds the created message in a live region that was in the DOM before Confirm", async () => {
    previewImport.mockResolvedValue(PREVIEW);
    confirmImport.mockResolvedValue({ slug: "area", version: 4 });
    const { container } = render(RateTableImportExport, { props });
    const before = liveRegions(container);
    await pick();
    await userEvent.click(screen.getByRole("button", { name: "Check file" }));
    await userEvent.click(await screen.findByRole("button", { name: "Confirm and create version" }));
    await screen.findByText("Created area@4");
    const holder = liveRegions(container).find((el) => /Created area@4/.test(el.textContent ?? ""));
    expect(holder).toBeDefined();
    expect(before).toContain(holder);
  });
});
