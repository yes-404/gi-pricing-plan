import userEvent from "@testing-library/user-event";
import { render, screen, waitFor, within } from "@testing-library/vue";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ProblemError } from "@/api/problem";

import RateTableEditorView from "../RateTableEditorView.vue";

const getRatingVersionByRef = vi.fn();
const getRateTable = vi.fn();
const getCellPage = vi.fn();
const previewEdit = vi.fn();
const confirmEdit = vi.fn();

vi.mock("@/api/ratingVersions", () => ({
  getRatingVersionByRef: (...args: unknown[]) => getRatingVersionByRef(...args),
}));
vi.mock("@/api/rateTables", () => ({
  getRateTable: (...args: unknown[]) => getRateTable(...args),
  getCellPage: (...args: unknown[]) => getCellPage(...args),
  previewEdit: (...args: unknown[]) => previewEdit(...args),
  confirmEdit: (...args: unknown[]) => confirmEdit(...args),
}));

const RATING = {
  id: "01a04394-338b-7651-9e42-c73ee70396f8",
  slug: "fremtpl2-demo",
  version: 1,
  pins: { rate_tables: ["rate_table:area@3", "rate_table:band@2"] },
};
const TABLE = {
  slug: "area",
  version: 3,
  rateable: true,
  storage: "rows",
  keys: [{ name: "area", type: "string" }],
  value: { name: "relativity", type: "relativity", unit: "factor" },
};
const PAGE_ONE = {
  items: [
    { area: "A", relativity: "1.0000" },
    { area: "B", relativity: "1.1000" },
  ],
  next_cursor: "C1",
  total_estimate: 3,
};
const PAGE_TWO = { items: [{ area: "C", relativity: "1.2000" }], next_cursor: null, total_estimate: 3 };
const props = { slug: "fremtpl2-demo", version: "1", tableSlug: "area" };
const mounted = { global: { stubs: { RouterLink: { template: "<a><slot /></a>" } } } };

beforeEach(() => {
  vi.resetAllMocks();
  getRatingVersionByRef.mockResolvedValue(RATING);
  getRateTable.mockResolvedValue(TABLE);
  getCellPage.mockImplementation(async (_ref: string, cursor?: string) =>
    cursor === "C1" ? PAGE_TWO : PAGE_ONE,
  );
});

const cells = (): HTMLElement[] => screen.getAllByRole("textbox", { name: /relativity for/ });

async function typeInto(name: RegExp, text: string): Promise<void> {
  const input = screen.getByRole("textbox", { name });
  await userEvent.clear(input);
  await userEvent.type(input, text);
}

describe("RateTableEditorView: reading the table (FR-228, FR-232, RL-1475 item 3)", () => {
  it("resolves the table through the Rating Version's pins, with no list call", async () => {
    render(RateTableEditorView, { props, ...mounted });

    await screen.findAllByRole("textbox", { name: /relativity for/ });
    expect(cells()).toHaveLength(2);
    expect(getRatingVersionByRef).toHaveBeenCalledExactlyOnceWith("fremtpl2-demo", 1);
    expect(getRateTable).toHaveBeenCalledExactlyOnceWith("area@3");
    expect(getCellPage).toHaveBeenCalledExactlyOnceWith("area@3", undefined);
  });

  it("says so, and reads no table, when the Rating Version does not pin the table", async () => {
    render(RateTableEditorView, { props: { ...props, tableSlug: "other" }, ...mounted });

    expect(await screen.findByRole("alert")).toHaveTextContent(/does not pin/i);
    expect(getRateTable).not.toHaveBeenCalled();
  });

  it("follows the server's cursor with Next and Previous, and never reads ahead", async () => {
    render(RateTableEditorView, { props, ...mounted });
    await screen.findAllByRole("textbox");
    expect(getCellPage).toHaveBeenCalledTimes(1); // no second page before the user asks

    await userEvent.click(screen.getByRole("button", { name: "Next page" }));
    await waitFor(() => expect(cells()).toHaveLength(1));
    expect(getCellPage).toHaveBeenLastCalledWith("area@3", "C1");
    expect(screen.getByRole("button", { name: "Next page" })).toBeDisabled();

    await userEvent.click(screen.getByRole("button", { name: "Previous page" }));
    await waitFor(() => expect(cells()).toHaveLength(2));
    expect(getCellPage).toHaveBeenLastCalledWith("area@3", undefined);
  });
});

describe("RateTableEditorView: the edit flow (FR-229, FR-231, FR-234)", () => {
  it("keeps save disabled until there is an edit and a non-blank change note", async () => {
    render(RateTableEditorView, { props, ...mounted });
    await screen.findAllByRole("textbox");
    const save = screen.getByRole("button", { name: "Review changes" });
    expect(save).toBeDisabled();

    await typeInto(/relativity for area A/, "1.0500");
    expect(save).toBeDisabled(); // an edit, but no note

    await userEvent.type(screen.getByLabelText("Change note"), "   ");
    expect(save).toBeDisabled(); // a blank note is no note

    await userEvent.type(screen.getByLabelText("Change note"), "area A +5%");
    expect(save).toBeEnabled();
  });

  it("previews with the full edited row, shows the diff, then confirms and loads the new version", async () => {
    previewEdit.mockResolvedValue({ changed_cells: 1, max_abs_change_pct: "5" });
    confirmEdit.mockResolvedValue({ ...TABLE, version: 4 });
    getRateTable.mockResolvedValueOnce(TABLE).mockResolvedValue({ ...TABLE, version: 4 });
    render(RateTableEditorView, { props, ...mounted });
    await screen.findAllByRole("textbox");

    await typeInto(/relativity for area A/, "1.0500");
    await userEvent.type(screen.getByLabelText("Change note"), "area A +5%");
    await userEvent.click(screen.getByRole("button", { name: "Review changes" }));

    const body = {
      base_version: 3,
      change_note: "area A +5%",
      edits: [{ area: "A", relativity: "1.0500" }],
    };
    expect(previewEdit).toHaveBeenCalledExactlyOnceWith("area", body);
    const diff = await screen.findByRole("region", { name: "Changes to confirm" });
    expect(within(diff).getByText(/1 cell changed/i)).toBeInTheDocument();
    expect(within(diff).getByText(/1\.0000/)).toBeInTheDocument();
    expect(within(diff).getByText(/1\.0500/)).toBeInTheDocument();
    expect(confirmEdit).not.toHaveBeenCalled();

    await userEvent.click(screen.getByRole("button", { name: "Confirm and create version" }));
    expect(confirmEdit).toHaveBeenCalledExactlyOnceWith("area", body);
    await waitFor(() => expect(getRateTable).toHaveBeenLastCalledWith("area@4"));
    expect(await screen.findByText(/created area@4/i)).toBeInTheDocument();
  });

  it("marks each cell a 422 names, and keeps the edit", async () => {
    previewEdit.mockRejectedValue(
      new ProblemError({
        type: "x",
        title: "Manual edit refused",
        status: 422,
        code: "RATE_TABLE_INCOMPLETE",
        errors: [{ field: "edits.0.relativity", code: "OUT_OF_BOUNDS", message: "below the minimum" }],
      }),
    );
    render(RateTableEditorView, { props, ...mounted });
    await screen.findAllByRole("textbox");
    await typeInto(/relativity for area A/, "-1");
    await userEvent.type(screen.getByLabelText("Change note"), "x");
    await userEvent.click(screen.getByRole("button", { name: "Review changes" }));

    const cell = await screen.findByRole("textbox", { name: /relativity for area A/ });
    await waitFor(() => expect(cell).toHaveAttribute("aria-invalid", "true"));
    expect(cell).toHaveValue("-1");
    expect(screen.getByText(/below the minimum/)).toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: /relativity for area B/ })).toHaveAttribute(
      "aria-invalid",
      "false",
    );
  });

  it("shows a refusal that names no cell, such as a stale base, as an alert", async () => {
    previewEdit.mockRejectedValue(
      new ProblemError({
        type: "x",
        title: "Rate table version already exists",
        status: 409,
        code: "VALIDATION_FAILED",
        detail: "area@4 already exists in this workspace.",
      }),
    );
    render(RateTableEditorView, { props, ...mounted });
    await screen.findAllByRole("textbox");
    await typeInto(/relativity for area A/, "1.5");
    await userEvent.type(screen.getByLabelText("Change note"), "x");
    await userEvent.click(screen.getByRole("button", { name: "Review changes" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/already exists/);
  });

  it("FR-1186: shows no approval, lifecycle or status text for a Rate Table Version", async () => {
    const { container } = render(RateTableEditorView, { props, ...mounted });
    await screen.findAllByRole("textbox");
    expect(container.textContent ?? "").not.toMatch(/approv|lifecycle|status|draft|pending/i);
  });
});
