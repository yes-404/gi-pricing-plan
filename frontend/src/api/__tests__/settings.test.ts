import { afterEach, describe, expect, it, vi } from "vitest";

import { ProblemError } from "../problem";
import { listSettings, updateSetting, type SettingResolution } from "../settings";

// Annotated with the generated type, so a `model-schema` change to the resolution fails
// `type-check` here rather than leaving a fixture for a shape the API no longer sends.
const RESOLUTION: SettingResolution = {
  key: "validation.psi_warn_threshold",
  effective_value: 0.1,
  resolved_from: "workspace",
  candidates: [
    { source: "env", value: null },
    { source: "workspace", value: 0.1 },
    { source: "default", value: 0.1 },
  ],
  type: "float",
  constraints: { min: 0, max: 1 },
  feature_flag: false,
  description: "",
  scope: "workspace",
};

function respond(status: number, body: unknown): void {
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

afterEach(() => vi.unstubAllGlobals());

describe("the settings client", () => {
  it("reads the resolutions with GET /settings", async () => {
    respond(200, [RESOLUTION]);
    await expect(listSettings()).resolves.toEqual([RESOLUTION]);
    const [url, init] = vi.mocked(fetch).mock.calls[0]!;
    expect(String(url)).toMatch(/\/api\/v1\/settings$/);
    expect(init?.method).toBe("GET");
  });

  it("sends one PUT carrying exactly the one edited key", async () => {
    respond(200, [RESOLUTION]);
    await updateSetting("validation.psi_warn_threshold", 0.2);
    const [url, init] = vi.mocked(fetch).mock.calls[0]!;
    expect(String(url)).toMatch(/\/api\/v1\/settings$/);
    expect(init?.method).toBe("PUT");
    expect(JSON.parse(String(init?.body))).toEqual({
      values: { "validation.psi_warn_threshold": 0.2 },
    });
  });

  it("surfaces a 422 as a ProblemError whose detail is the server's text, unparsed", async () => {
    const detail = "validation.psi_warn_threshold: 7 violates {'min': 0, 'max': 1}.";
    respond(422, {
      type: "about:blank",
      title: "Setting value is out of range",
      status: 422,
      code: "SETTING_INVALID",
      detail,
      errors: [],
    });
    const error = await updateSetting("validation.psi_warn_threshold", 7).catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ProblemError);
    expect((error as ProblemError).problem.detail).toBe(detail);
  });
});
