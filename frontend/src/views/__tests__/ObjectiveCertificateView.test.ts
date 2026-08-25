import { render, screen } from "@testing-library/vue";
import { afterEach, describe, expect, it, vi } from "vitest";

import * as api from "@/api/objectives";
import { ProblemError } from "@/api/problem";
import ObjectiveCertificateView from "../ObjectiveCertificateView.vue";

// Field names read out of the generated contract: `CertificateResult` requires
// `checks`/`sampling`/`overall`, `CertificateCheck` is name/status/detail, and
// `CertificateOutcome` is certified | certified_with_findings | failed.
const CERTIFICATE = {
  id: "c1",
  custom_objective_id: "a1",
  objective_version: 2,
  certified_at: "2026-08-25T00:00:00Z",
  job_id: "j1",
  result: {
    // Deliberately ordered so that EVERY plausible sort reorders it, and the violated check
    // sits in the middle rather than first. Found by mutation: with `violated` first,
    // "group the findings to the top" reproduced this order exactly and the order assertion
    // passed while the property it names was gone.
    //   violated to top    -> convexity, finiteness, boundedness
    //   violated to bottom -> finiteness, boundedness, convexity
    //   alphabetical       -> boundedness, convexity, finiteness
    // None of those is the artifact order below.
    checks: [
      { name: "finiteness", status: "pass", detail: "finite throughout" },
      { name: "convexity", status: "violated", detail: "hessian negative on 4% of sampled points" },
      { name: "boundedness", status: "pass", detail: "bounded on the sampled domain" },
    ],
    sampling: { n_points: 1000, seed: 7, y_range: [0, 10], f_range: [-5, 5], w_range: [1, 1] },
    overall: "certified_with_findings",
    library_versions: { xgboost: "2.1.0" },
  },
} as unknown as api.ObjectiveCertificate;

const OBJECTIVE = {
  id: "a1",
  slug: "tweedie-cap",
  version: 2,
  hessian_strategy: "clip_to_min",
  applicability: { responses: ["claim_count"], backends: ["xgboost"] },
} as unknown as api.CustomObjective;

function mountView() {
  return render(ObjectiveCertificateView, { props: { id: "a1" } });
}

afterEach(() => vi.restoreAllMocks());

describe("ObjectiveCertificateView", () => {
  /**
   * FR-MODEL-43 as amended 2026-08-25, and the discharge of FR-OVR-21's fourth carve-out.
   *
   * The amendment binds a surface: a view given `certified_with_findings` must not style,
   * label, group or order a `violated` check as a failure. This asserts all four limbs on a
   * certificate whose only finding *is* the `violated` one.
   */
  it("presents a violated check as a finding and not as a failure", async () => {
    vi.spyOn(api, "getObjectiveCertificate").mockResolvedValue(CERTIFICATE);
    vi.spyOn(api, "getObjective").mockResolvedValue(OBJECTIVE);
    const { container } = mountView();

    // Scoped to the verdict element: the strategy sentence below also contains the
    // phrase, and an unscoped query matches both.
    const verdict = await screen.findByText("Certified with findings", { selector: "strong" });
    expect(verdict).toBeInTheDocument();

    const text = (container.textContent ?? "").toLowerCase();
    // Label: the verdict is not a failure, and the row is not called one.
    expect(text).not.toContain("certification failed");
    // Style: the violated row's badge carries the finding tone, not the failure tone.
    const badges = Array.from(container.querySelectorAll("td span"));
    const violated = badges.find((b) => (b.textContent ?? "").includes("finding"));
    expect(violated?.className).not.toContain("rose");
  });

  it("shows each check's detail, which FR-MODEL-69 makes a reported finding", async () => {
    vi.spyOn(api, "getObjectiveCertificate").mockResolvedValue(CERTIFICATE);
    vi.spyOn(api, "getObjective").mockResolvedValue(OBJECTIVE);
    mountView();

    expect(
      await screen.findByText("hessian negative on 4% of sampled points"),
    ).toBeInTheDocument();
  });

  it("shows the declared clipping strategy beside a violated finding", async () => {
    // The amendment: "a finding without the strategy is the half an Approver cannot act on."
    vi.spyOn(api, "getObjectiveCertificate").mockResolvedValue(CERTIFICATE);
    vi.spyOn(api, "getObjective").mockResolvedValue(OBJECTIVE);
    mountView();

    expect(await screen.findByText(/clip_to_min/)).toBeInTheDocument();
  });

  it("says a certificate short of nine checks is incomplete", async () => {
    // FR-MODEL-126: nine checks always. Fewer is a failure of the run, not a smaller
    // certificate, so the count is stated rather than quietly rendered.
    vi.spyOn(api, "getObjectiveCertificate").mockResolvedValue(CERTIFICATE);
    vi.spyOn(api, "getObjective").mockResolvedValue(OBJECTIVE);
    const { container } = mountView();

    await screen.findByText("Certified with findings", { selector: "strong" });
    expect((container.textContent ?? "").toLowerCase()).toContain("3 of the 9");
  });

  it("treats a missing certificate as a normal state, not an error", async () => {
    // Measured, not guessed: `platform/objectives.py`'s `load_certificate` raises
    // PlatformError("NOT_FOUND", "This objective has not been certified", 404, …). The plan's
    // `OBJECTIVE_CERTIFICATE_NOT_FOUND` exists nowhere in the repository.
    vi.spyOn(api, "getObjective").mockResolvedValue(OBJECTIVE);
    vi.spyOn(api, "getObjectiveCertificate").mockRejectedValue(
      new ProblemError({
        type: "about:blank",
        code: "NOT_FOUND",
        title: "This objective has not been certified",
        detail: "No certificate for objective a1.",
        status: 404,
      } as never),
    );
    mountView();

    expect(await screen.findByText(/has not been certified yet/i)).toBeInTheDocument();
  });

  it("does not read an unrelated refusal as 'not certified'", async () => {
    // The control for the branch above. `instanceof ProblemError` alone would render a 403 as
    // "not certified yet" — a false statement about the artifact. Several codes share 404, so
    // the branch is on the code.
    vi.spyOn(api, "getObjective").mockResolvedValue(OBJECTIVE);
    vi.spyOn(api, "getObjectiveCertificate").mockRejectedValue(
      new ProblemError({
        type: "about:blank",
        code: "PERMISSION_DENIED",
        title: "Forbidden",
        detail: "model:read required.",
        status: 403,
      } as never),
    );
    const { container } = mountView();

    await screen.findByText(/model:read required/i);
    expect((container.textContent ?? "").toLowerCase()).not.toContain("has not been certified yet");
  });

  it("renders the checks in the artifact's order, never grouped or sorted by status", () => {
    // The **group** and **order** limbs of the amended FR-MODEL-43. The other two limbs are
    // covered by the tone and label assertions; these two hold only because the template
    // iterates `checks` directly, and "enforced by construction" is not enforced — a `sort`
    // added later would pass every other test in this file.
    //
    // Sorting findings to the top or bottom is the subtler failure: it never labels anything
    // a failure, but it segregates the `violated` row into a block a reader parses as the
    // problems, which is the "group … as a failure" the amendment names.
    vi.spyOn(api, "getObjectiveCertificate").mockResolvedValue(CERTIFICATE);
    vi.spyOn(api, "getObjective").mockResolvedValue(OBJECTIVE);
    const { container } = mountView();

    return screen.findByText("Certified with findings", { selector: "strong" }).then(() => {
      const rendered = Array.from(container.querySelectorAll("tbody tr td:first-child")).map(
        (cell) => (cell.textContent ?? "").trim(),
      );
      expect(rendered).toEqual(["finiteness", "convexity", "boundedness"]);
    });
  });
});
