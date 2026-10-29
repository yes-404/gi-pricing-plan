import userEvent from "@testing-library/user-event";
import { render, screen } from "@testing-library/vue";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ProblemError } from "@/api/problem";

import BulkOperationDialog from "../BulkOperationDialog.vue";

const bulkOperation = vi.fn();

vi.mock("@/api/rateTables", () => ({
  bulkOperation: (...args: unknown[]) => bulkOperation(...args),
}));

beforeEach(() => {
  vi.resetAllMocks();
  bulkOperation.mockResolvedValue({ slug: "area", version: 4 });
});

const props = { tableRef: "area@3" };

describe("BulkOperationDialog (FR-233)", () => {
  it("offers the four operations, the whole-table uplift first", () => {
    render(BulkOperationDialog, { props });
    const kinds = screen.getAllByRole("option").map((option) => option.textContent?.trim());
    expect(kinds).toEqual([
      "Uplift the whole table",
      "Uplift the cells a key filter selects",
      "Floor and cap the values",
      "Rebase to a base level",
    ]);
  });

  it("posts the typed percentage as a string and tells the caller the new version", async () => {
    const { emitted } = render(BulkOperationDialog, { props });
    await userEvent.type(screen.getByLabelText("Percentage"), "5.000000000000000001");
    await userEvent.click(screen.getByRole("button", { name: "Apply" }));
    expect(bulkOperation).toHaveBeenCalledWith("area@3", {
      kind: "uplift_table",
      parameters: { percentage: "5.000000000000000001" },
    });
    await screen.findByText("Created area@4");
    expect(emitted().created).toEqual([[{ slug: "area", version: 4 }]]);
  });

  it("shows only the fields the chosen operation takes", async () => {
    render(BulkOperationDialog, { props });
    await userEvent.selectOptions(screen.getByLabelText("Operation"), "floor_and_cap");
    expect(screen.getByLabelText("Floor")).toBeInTheDocument();
    expect(screen.getByLabelText("Cap")).toBeInTheDocument();
    expect(screen.queryByLabelText("Percentage")).toBeNull();
    await userEvent.type(screen.getByLabelText("Floor"), "0.8");
    await userEvent.type(screen.getByLabelText("Cap"), "1.5");
    await userEvent.click(screen.getByRole("button", { name: "Apply" }));
    expect(bulkOperation).toHaveBeenCalledWith("area@3", {
      kind: "floor_and_cap",
      parameters: { floor: "0.8", cap: "1.5" },
    });
  });

  it("types a key filter one key column per line", async () => {
    render(BulkOperationDialog, { props });
    await userEvent.selectOptions(screen.getByLabelText("Operation"), "uplift_by_filter");
    await userEvent.type(screen.getByLabelText("Percentage"), "3");
    await userEvent.type(screen.getByLabelText("Key filter"), "area: A, B");
    await userEvent.click(screen.getByRole("button", { name: "Apply" }));
    expect(bulkOperation).toHaveBeenCalledWith("area@3", {
      kind: "uplift_by_filter",
      parameters: { percentage: "3", filter: { area: ["A", "B"] } },
    });
  });

  it("names a missing value and sends nothing", async () => {
    render(BulkOperationDialog, { props });
    await userEvent.click(screen.getByRole("button", { name: "Apply" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("percentage is required");
    expect(bulkOperation).not.toHaveBeenCalled();
  });

  it("shows the platform's own refusal, such as a result that leaves the value's bounds", async () => {
    bulkOperation.mockRejectedValueOnce(
      new ProblemError({
        type: "about:blank",
        title: "Validation failed",
        status: 422,
        code: "VALIDATION_FAILED",
        detail: "The uplift would take 2 cells above the declared maximum.",
        errors: [],
      }),
    );
    render(BulkOperationDialog, { props });
    await userEvent.type(screen.getByLabelText("Percentage"), "500");
    await userEvent.click(screen.getByRole("button", { name: "Apply" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("above the declared maximum");
  });
});

// NFR-463 / WCAG 4.1.3 (FD-1959 F3): a status message is announced only if its live region is in
// the DOM before the message arrives. A region that mounts together with its text (v-if) is not.
const liveRegions = (root: Element): Element[] =>
  Array.from(root.querySelectorAll('[role="status"], [aria-live="polite"]'));

describe("BulkOperationDialog: the status region is persistent (NFR-463, FD-1959 F3)", () => {
  it("holds the created message in a live region that was in the DOM before Apply", async () => {
    const { container } = render(BulkOperationDialog, { props });
    const before = liveRegions(container);
    await userEvent.type(screen.getByLabelText("Percentage"), "5");
    await userEvent.click(screen.getByRole("button", { name: "Apply" }));
    await screen.findByText("Created area@4");
    const holder = liveRegions(container).find((el) => /Created area@4/.test(el.textContent ?? ""));
    expect(holder).toBeDefined();
    expect(before).toContain(holder);
  });
});
