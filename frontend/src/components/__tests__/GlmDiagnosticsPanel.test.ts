import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import type { GlmDiagnostics } from "@/api/diagnostics";

import GlmDiagnosticsPanel from "../GlmDiagnosticsPanel.vue";

const GLM: GlmDiagnostics = {
  deviance: 41_233.7,
  null_deviance: 45_902.1,
  aic: 41_261.7,
  bic: 41_402.9,
  dispersion: 1.04,
  degrees_of_freedom: 407_516,
  type_iii_tests: [
    { factor: "vehicle_age", deviance_delta: 812.4, df: 3, p_value: 0.0 },
    { factor: "region", deviance_delta: 4.1, df: 2, p_value: 0.128 },
  ],
  aliasing: ["region_north:vehicle_age_0_3"],
  vif: { vehicle_age: 1.2, region: 8.7 },
  residual_blob: null,
  leverage_blob: null,
};

describe("GlmDiagnosticsPanel", () => {
  it("shows the fit statistics", () => {
    render(GlmDiagnosticsPanel, { props: { glm: GLM } });
    const row = screen.getByRole("row", { name: /^Deviance/ });
    expect(within(row).getAllByRole("cell")[0]).toHaveTextContent("41233.7");
  });

  /**
   * `aic` is `float | None`, and the source says why: a Tweedie fit has no closed-form
   * likelihood this platform evaluates, so an absent AIC is a fact about the family rather
   * than a gap in the record. Rendered as `0` it would read as a fit with a perfect
   * likelihood — the one reading the field exists to prevent.
   */
  it("renders a null AIC as an em dash and not as a zero", () => {
    render(GlmDiagnosticsPanel, { props: { glm: { ...GLM, aic: null } } });
    const row = screen.getByRole("row", { name: /AIC/ });
    expect(within(row).getAllByRole("cell")[0]).toHaveTextContent("—");
    expect(within(row).getAllByRole("cell")[0]).not.toHaveTextContent("0");
  });

  it("lists each type-III test with its p-value", () => {
    render(GlmDiagnosticsPanel, { props: { glm: GLM } });
    const table = screen.getByRole("table", { name: /type III/i });
    expect(within(table).getAllByRole("row")).toHaveLength(GLM.type_iii_tests.length + 1);
    const row = within(table).getByRole("row", { name: /region/ });
    expect(within(row).getAllByRole("cell")[2]).toHaveTextContent("0.128");
  });

  it("lists each aliased term by its bare name", () => {
    render(GlmDiagnosticsPanel, { props: { glm: GLM } });
    expect(screen.getByText("region_north:vehicle_age_0_3")).toBeInTheDocument();
  });

  it("says so when nothing was aliased, rather than rendering an empty list", () => {
    render(GlmDiagnosticsPanel, { props: { glm: { ...GLM, aliasing: [] } } });
    expect(screen.getByText(/no terms were aliased/i)).toBeInTheDocument();
  });

  /**
   * Two states, not one, and the plan's single test conflated them: it asserts "not
   * retrievable" against a fixture whose `residual_blob` is `null`, which the panel reports
   * as "not recorded by this fit" — a different fact about a different fit. A reference the
   * fit never wrote and a reference no read resolves yet are distinguishable in the contract
   * and would be acted on differently, so each is asserted where it applies.
   */
  it("says a series this fit never recorded was not recorded, rather than drawing it empty", () => {
    render(GlmDiagnosticsPanel, { props: { glm: GLM } });
    expect(screen.getByText(/Residuals: not recorded by this fit/i)).toBeInTheDocument();
  });

  it("says a recorded series is not retrievable yet, rather than offering a link to nothing", () => {
    render(GlmDiagnosticsPanel, {
      props: { glm: { ...GLM, residual_blob: "blob://residuals/9f2c" } },
    });
    expect(screen.getByText(/Residuals: recorded, not retrievable yet/i)).toBeInTheDocument();
    expect(screen.queryByRole("link")).not.toBeInTheDocument();
  });

  /**
   * `type_iii_tests` and `vif` both default to empty in the contract, exactly as `aliasing`
   * does. A table rendered with a header and no rows reads as "tested, nothing to report";
   * absent is what it actually means. The rule the plan applies to `aliasing` is the same
   * rule, and these two fields default the same way.
   */
  it("says no type-III tests were recorded rather than showing a header over nothing", () => {
    render(GlmDiagnosticsPanel, { props: { glm: { ...GLM, type_iii_tests: [] } } });
    expect(screen.queryByRole("table", { name: /type III/i })).not.toBeInTheDocument();
    expect(screen.getByText(/no type-III tests were recorded/i)).toBeInTheDocument();
  });

  it("says no variance inflation was recorded rather than showing a header over nothing", () => {
    render(GlmDiagnosticsPanel, { props: { glm: { ...GLM, vif: {} } } });
    expect(screen.queryByRole("table", { name: /variance inflation/i })).not.toBeInTheDocument();
    expect(screen.getByText(/no variance inflation factors were recorded/i)).toBeInTheDocument();
  });
});
