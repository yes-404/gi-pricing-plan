import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import { ARTIFACT } from "@/views/__tests__/fixtures";

import TransparencyPanel from "../TransparencyPanel.vue";

describe("the transparency panel", () => {
  it("puts the fidelity statement where it cannot be missed", () => {
    // FR-MODEL-34: the approximation is what makes a booster rateable as a table, and the
    // fidelity statement is where it says where it stops being one.
    render(TransparencyPanel, { props: { artifact: ARTIFACT, state: "ready" } });
    expect(screen.getByText(/under-price/i)).toBeInTheDocument();
  });

  it("distinguishes monotonicity not assessed from monotonicity not verified", () => {
    // `monotonicity_verified` is boolean or null. Rendered as a two-state badge, "not checked"
    // is reported as "failed" or as "passed" — either way it asserts a check nobody ran.
    render(TransparencyPanel, {
      props: { artifact: { ...ARTIFACT, monotonicity_verified: null }, state: "ready" },
    });
    expect(screen.getByText(/not assessed/i)).toBeInTheDocument();
  });

  it("does not call an unassessed monotonicity a failed one", () => {
    render(TransparencyPanel, {
      props: { artifact: { ...ARTIFACT, monotonicity_verified: false }, state: "ready" },
    });
    expect(screen.getByText(/not verified/i)).toBeInTheDocument();
    expect(screen.queryByText(/not assessed/i)).toBeNull();
  });

  it("says so when monotonicity was verified", () => {
    render(TransparencyPanel, {
      props: { artifact: { ...ARTIFACT, monotonicity_verified: true }, state: "ready" },
    });
    expect(screen.getByText(/^verified$/i)).toBeInTheDocument();
  });

  it("shows each worst region with the exposure it covers", () => {
    render(TransparencyPanel, { props: { artifact: ARTIFACT, state: "ready" } });
    const table = screen.getByRole("table", { name: "Where the approximation is worst" });
    expect(within(table).getByText(/0\.8\s*%/)).toBeInTheDocument();
  });

  it("reads a missing artifact as a state, never as a failure", () => {
    // FR-MODEL-33 makes the artifact an obligation for a non-GLM model. Not having one yet is
    // a thing to say, not an error banner: the red box is for a call that went wrong.
    render(TransparencyPanel, { props: { artifact: null, state: "absent" } });
    expect(screen.getByText(/no transparency artifact/i)).toBeInTheDocument();
    expect(screen.queryByRole("alert")).toBeNull();
  });

  it("renders no approximation block when the artifact carries none", () => {
    // FR-MODEL-33 allows any combination of the three blocks, so an absent block is not a
    // gap — and an empty table headed "Where the approximation is worst" says there is an
    // approximation and it is perfect everywhere.
    render(TransparencyPanel, {
      props: { artifact: { ...ARTIFACT, glm_approximation: null }, state: "ready" },
    });
    expect(screen.queryByRole("table", { name: "Where the approximation is worst" })).toBeNull();
    expect(screen.getByText(/under-price/i)).toBeInTheDocument();
  });

  it("names the SHAP sample and seed, not just the ranking", () => {
    // A mean absolute contribution is a statistic of a sample. Ranked without the sample size
    // and the seed it is a ranking nobody can reproduce or bound.
    render(TransparencyPanel, { props: { artifact: ARTIFACT, state: "ready" } });
    expect(screen.getByText(/tree_shap/)).toBeInTheDocument();
    expect(screen.getByText(/20,000/)).toBeInTheDocument();
    expect(screen.getByText(/seed 7/i)).toBeInTheDocument();
  });
});
