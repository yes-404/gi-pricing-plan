import { fireEvent, render, screen, waitFor, within } from "@testing-library/vue";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ProblemError } from "@/api/problem";
import type { SettingResolution } from "@/api/settings";

import SettingsView from "../SettingsView.vue";

const listSettings = vi.fn();
const updateSetting = vi.fn();

vi.mock("@/api/settings", () => ({
  listSettings: (...args: unknown[]) => listSettings(...args),
  updateSetting: (...args: unknown[]) => updateSetting(...args),
}));

// Annotated with the generated type: the fixtures are bound to the contract.
const PSI: SettingResolution = {
  key: "validation.psi_warn_threshold",
  effective_value: 0.1,
  resolved_from: "workspace",
  candidates: [
    { source: "env", value: null },
    { source: "workspace", value: 0.1 },
    { source: "default", value: 0.25 },
  ],
  type: "float",
  constraints: { min: 0, max: 1 },
  feature_flag: false,
  description: "",
  scope: "workspace",
};

const FROM_ENV: SettingResolution = {
  key: "rating.trace_sample_rate",
  effective_value: 0.5,
  resolved_from: "env",
  candidates: [
    { source: "env", value: 0.5 },
    { source: "workspace", value: 0.2 },
    { source: "default", value: 0.01 },
  ],
  type: "float",
  constraints: { min: 0, max: 1 },
  feature_flag: false,
  description: "",
  scope: "workspace_or_environment",
};

const ENVIRONMENT_ONLY: SettingResolution = {
  key: "features.shadow_scoring_enabled",
  effective_value: false,
  resolved_from: "default",
  candidates: [{ source: "default", value: false }],
  type: "bool",
  constraints: {},
  feature_flag: true,
  description: "",
  scope: "environment",
};

// Keys read from the registry (`backend/src/app/platform/settings.py`), with the type, the
// constraints and the scope it declares. The first is a float whose minimum is 0, unset by
// default; the other two are integers for which 0 is out of range (`min` 396 and `min` 1).
const BATCH_ABORT: SettingResolution = {
  key: "rating.batch_abort_failure_rate",
  effective_value: null,
  resolved_from: "default",
  candidates: [
    { source: "env", value: null },
    { source: "workspace", value: null },
    { source: "default", value: null },
  ],
  type: "float",
  constraints: { min: 0, max: 1 },
  feature_flag: false,
  description: "",
  scope: "workspace",
};

const JOB_HISTORY: SettingResolution = {
  key: "retention.job_history_days",
  effective_value: 400,
  resolved_from: "default",
  candidates: [
    { source: "env", value: null },
    { source: "workspace", value: null },
    { source: "default", value: 400 },
  ],
  type: "int",
  constraints: { min: 396 },
  feature_flag: false,
  description: "",
  scope: "workspace",
};

const MAX_FACTORS: SettingResolution = {
  key: "modelling.max_factor_count",
  effective_value: null,
  resolved_from: "default",
  candidates: [
    { source: "env", value: null },
    { source: "workspace", value: null },
    { source: "default", value: null },
  ],
  type: "int",
  constraints: { min: 1 },
  feature_flag: false,
  description: "",
  scope: "workspace",
};

async function rowOf(key: string): Promise<HTMLElement> {
  return screen.findByRole("row", { name: new RegExp(key.replaceAll(".", "\\.")) });
}

beforeEach(() => {
  listSettings.mockReset();
  updateSetting.mockReset();
  listSettings.mockResolvedValue([PSI, FROM_ENV, ENVIRONMENT_ONLY]);
});

describe("the Settings view", () => {
  // FR-446, quoted verbatim from 07 §3.8 (markdown as written in the spec):
  //   Settings resolve by precedence: **environment variable → workspace setting → platform default**. The effective value and its source are inspectable by an Admin.
  //   The precedence is **process environment variable (`GIP_SETTING_<KEY>`) → Environment setting → workspace setting → platform default**.
  it("FR-446: a key resolved from env shows the environment variable as its source and has no edit control", async () => {
    render(SettingsView);
    const envRow = within(await rowOf("rating.trace_sample_rate"));
    // The Source column (third cell); the candidates list names the layer again.
    const source = envRow.getAllByRole("cell")[2]!;
    expect(source).toHaveTextContent(/^environment variable \(GIP_SETTING_<KEY>\)$/i);
    expect(envRow.queryByRole("button", { name: /edit/i })).not.toBeInTheDocument();
    expect(envRow.queryByRole("textbox")).not.toBeInTheDocument();
    expect(envRow.queryByRole("spinbutton")).not.toBeInTheDocument();
  });

  it("FR-446: a workspace-resolved key shows its source and offers an edit control", async () => {
    render(SettingsView);
    const psiRow = within(await rowOf("validation.psi_warn_threshold"));
    expect(psiRow.getAllByRole("cell")[2]).toHaveTextContent(/^workspace setting$/i);
    expect(psiRow.getByRole("button", { name: /edit/i })).toBeInTheDocument();
  });

  it("FR-446: shows every layer's candidate, not only the winner", async () => {
    render(SettingsView);
    const envRow = within(await rowOf("rating.trace_sample_rate"));
    expect(envRow.getByText(/workspace setting/i)).toBeInTheDocument();
    expect(envRow.getByText(/platform default/i)).toBeInTheDocument();
  });

  it("shows each setting's scope from the resolution, and offers no workspace edit to an environment-only setting", async () => {
    render(SettingsView);
    const psiRow = within(await rowOf("validation.psi_warn_threshold"));
    const envRow = within(await rowOf("rating.trace_sample_rate"));
    const envOnly = within(await rowOf("features.shadow_scoring_enabled"));
    expect(psiRow.getByText(/^workspace only$/i)).toBeInTheDocument();
    expect(envRow.getByText(/^workspace or environment$/i)).toBeInTheDocument();
    expect(envOnly.getByText(/^environment only$/i)).toBeInTheDocument();
    expect(envOnly.queryByRole("button", { name: /edit/i })).not.toBeInTheDocument();
  });

  it("FR-446: a 422 from PUT shows the server's error on that key's row, unparsed", async () => {
    const detail = "validation.psi_warn_threshold: 7.0 violates {'min': 0.0, 'max': 1.0}.";
    updateSetting.mockRejectedValue(
      new ProblemError({
        type: "about:blank",
        title: "Setting value is out of range",
        status: 422,
        code: "SETTING_INVALID",
        detail,
        errors: [],
      }),
    );
    const user = userEvent.setup();
    render(SettingsView);
    const psiRow = within(await rowOf("validation.psi_warn_threshold"));
    await user.click(psiRow.getByRole("button", { name: /edit/i }));
    const input = psiRow.getByRole("spinbutton");
    await user.clear(input);
    await user.type(input, "7");
    await user.click(psiRow.getByRole("button", { name: /save/i }));

    await waitFor(() => expect(updateSetting).toHaveBeenCalledWith("validation.psi_warn_threshold", 7));
    // The detail, verbatim, in an alert inside the row that was edited and no other.
    expect(await psiRow.findByRole("alert")).toHaveTextContent(detail);
    expect(within(await rowOf("rating.trace_sample_rate")).queryByRole("alert")).not.toBeInTheDocument();
  });

  it("replaces the list with the PUT response on success and offers no way to clear", async () => {
    updateSetting.mockResolvedValue([{ ...PSI, effective_value: 0.2 }, FROM_ENV, ENVIRONMENT_ONLY]);
    const user = userEvent.setup();
    render(SettingsView);
    const psiRow = within(await rowOf("validation.psi_warn_threshold"));
    await user.click(psiRow.getByRole("button", { name: /edit/i }));
    const input = psiRow.getByRole("spinbutton");
    await user.clear(input);
    await user.type(input, "0.2");
    await user.click(psiRow.getByRole("button", { name: /save/i }));
    await waitFor(() => expect(updateSetting).toHaveBeenCalledWith("validation.psi_warn_threshold", 0.2));
    await waitFor(async () =>
      expect(within(await rowOf("validation.psi_warn_threshold")).getAllByText("0.2").length).toBeGreaterThan(0),
    );
    expect(screen.queryByRole("button", { name: /clear|remove|reset/i })).not.toBeInTheDocument();
  });

  it("shows a refused read as an alert", async () => {
    listSettings.mockRejectedValue(
      new ProblemError({
        type: "about:blank",
        title: "Forbidden",
        status: 403,
        code: "PERMISSION_DENIED",
        detail: "settings:read needed.",
        errors: [],
      }),
    );
    render(SettingsView);
    expect(await screen.findByRole("alert")).toHaveTextContent("settings:read needed.");
  });
});

// The requirement id these tests hold (`07` §3.8).
const FR_446 = "FR-446";

/** The fixed refusal the view shows, before any request, for a number setting's empty or
 * non-numeric draft. */
const REFUSAL = /enter a number/i;

/**
 * Put `text` in the number input as the draft. A number input drops what is not a number
 * before the view sees it, so for "  " and "abc" the input is made a text input first: the
 * view must refuse whatever draft reaches it, not only what a browser lets through.
 */
async function draft(input: HTMLElement, text: string): Promise<void> {
  (input as HTMLInputElement).type = "text";
  await fireEvent.update(input, text);
}

describe(`${FR_446}: a number or integer draft that is not a number is refused before any request`, () => {
  beforeEach(() => {
    listSettings.mockResolvedValue([BATCH_ABORT, JOB_HISTORY, MAX_FACTORS, PSI]);
    // A request that is made is answered, so a test that must send nothing fails on the call
    // it asserts about and not on an unanswered mock.
    updateSetting.mockResolvedValue([BATCH_ABORT, JOB_HISTORY, MAX_FACTORS, PSI]);
  });

  async function edit(key: string): Promise<{ row: ReturnType<typeof within>; input: HTMLElement }> {
    const user = userEvent.setup();
    render(SettingsView);
    const row = within(await rowOf(key));
    await user.click(row.getByRole("button", { name: /edit/i }));
    return { row, input: row.getByRole("spinbutton") };
  }

  it("a min-0 key cleared and saved sends nothing and shows the refusal", async () => {
    const user = userEvent.setup();
    const { row, input } = await edit("rating.batch_abort_failure_rate");
    await user.clear(input);
    await user.click(row.getByRole("button", { name: /save/i }));

    expect(await row.findByRole("alert")).toHaveTextContent(REFUSAL);
    expect(updateSetting).not.toHaveBeenCalled();
  });

  it("a key whose range excludes 0 (min 396), cleared and saved, sends nothing, not 0", async () => {
    const user = userEvent.setup();
    const { row, input } = await edit("retention.job_history_days");
    await user.clear(input);
    await user.click(row.getByRole("button", { name: /save/i }));

    expect(await row.findByRole("alert")).toHaveTextContent(REFUSAL);
    expect(updateSetting).not.toHaveBeenCalled();
  });

  it.each(["modelling.max_factor_count", "retention.job_history_days"])(
    "the integer key %s refuses an empty draft",
    async (key) => {
      const user = userEvent.setup();
      const { row, input } = await edit(key);
      await user.clear(input);
      await user.click(row.getByRole("button", { name: /save/i }));
      expect(await row.findByRole("alert")).toHaveTextContent(REFUSAL);
      expect(updateSetting).not.toHaveBeenCalled();
    },
  );

  it.each([
    ["an empty string", ""],
    ["whitespace only", "  "],
    ["a word", "abc"],
  ])("the integer key modelling.max_factor_count refuses %s as the draft", async (_name, text) => {
    const user = userEvent.setup();
    const { row, input } = await edit("modelling.max_factor_count");
    await draft(input, text);
    await user.click(row.getByRole("button", { name: /save/i }));

    expect(await row.findByRole("alert")).toHaveTextContent(REFUSAL);
    expect(updateSetting).not.toHaveBeenCalled();
  });

  it.each([
    ["an empty string", ""],
    ["whitespace only", "  "],
    ["a word", "abc"],
  ])("the float key rating.batch_abort_failure_rate refuses %s as the draft", async (_name, text) => {
    const user = userEvent.setup();
    const { row, input } = await edit("rating.batch_abort_failure_rate");
    await draft(input, text);
    await user.click(row.getByRole("button", { name: /save/i }));

    expect(await row.findByRole("alert")).toHaveTextContent(REFUSAL);
    expect(updateSetting).not.toHaveBeenCalled();
  });

  it("the refusal is on that key's row and no other", async () => {
    const user = userEvent.setup();
    const { row, input } = await edit("rating.batch_abort_failure_rate");
    await user.clear(input);
    await user.click(row.getByRole("button", { name: /save/i }));
    await row.findByRole("alert");
    expect(within(await rowOf("retention.job_history_days")).queryByRole("alert")).not.toBeInTheDocument();
  });

  it("a field cleared and then re-typed with a valid number saves exactly that number", async () => {
    const user = userEvent.setup();
    const { row, input } = await edit("rating.batch_abort_failure_rate");
    await user.clear(input);
    await user.click(row.getByRole("button", { name: /save/i }));
    await row.findByRole("alert");

    await user.type(input, "0.2");
    await user.click(row.getByRole("button", { name: /save/i }));

    await waitFor(() => expect(updateSetting).toHaveBeenCalledTimes(1));
    expect(updateSetting).toHaveBeenCalledWith("rating.batch_abort_failure_rate", 0.2);
  });

  it("an integer field cleared and then re-typed saves exactly that integer", async () => {
    const user = userEvent.setup();
    const { row, input } = await edit("retention.job_history_days");
    await user.clear(input);
    await user.click(row.getByRole("button", { name: /save/i }));
    await row.findByRole("alert");

    await user.type(input, "500");
    await user.click(row.getByRole("button", { name: /save/i }));

    await waitFor(() => expect(updateSetting).toHaveBeenCalledTimes(1));
    expect(updateSetting).toHaveBeenCalledWith("retention.job_history_days", 500);
    expect(row.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("a typed 0 on a min-0 key is a number and is sent as 0", async () => {
    const user = userEvent.setup();
    const { row, input } = await edit("rating.batch_abort_failure_rate");
    await user.clear(input);
    await user.type(input, "0");
    await user.click(row.getByRole("button", { name: /save/i }));

    await waitFor(() => expect(updateSetting).toHaveBeenCalledWith("rating.batch_abort_failure_rate", 0));
    expect(updateSetting).toHaveBeenCalledTimes(1);
  });
});
