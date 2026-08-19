import { render, screen } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import type { ColumnComparison } from "@/api/profiles";

import ColumnDrift from "../ColumnDrift.vue";

const MEASURED: ColumnComparison = {
  column: "veh_brand",
  psi: 0.31,
  mean_shift: null,
  null_rate_shift: 0.012,
  new_levels: ["B14"],
  vanished_levels: ["B7"],
};

describe("ColumnDrift", () => {
  it("renders nothing at all when no comparison is loaded", () => {
    // `undefined` is not "no drift" — it is "nobody asked". The card must look exactly as
    // it did before a reference was chosen.
    const { container } = render(ColumnDrift, { props: { drift: undefined } });
    expect(container.textContent?.trim()).toBe("");
  });

  it("says a column is new rather than showing it as unchanged", () => {
    // `compare_profiles` skips a column the reference profile does not have, so a missing
    // entry is a finding: the column did not exist in the version being compared against.
    render(ColumnDrift, { props: { drift: null } });
    expect(screen.getByText(/new in this version/)).toBeInTheDocument();
  });

  it("bands a PSI above VR-DST-1's fail threshold", () => {
    render(ColumnDrift, { props: { drift: MEASURED } });
    expect(screen.getByText(/PSI 0\.310/)).toHaveClass("text-red-700");
  });

  it("bands a PSI above VR-DST-1's warn threshold as shifted, not stable", () => {
    // Pins the band-name -> colour hop, not just psiBand's numeric boundaries (those are
    // covered in api/__tests__/profiles.test.ts). Swapping TONE.shifted and TONE.stable
    // would leave every other assertion in this file green.
    render(ColumnDrift, { props: { drift: { ...MEASURED, psi: 0.11 } } });
    expect(screen.getByText(/PSI 0\.110/)).toHaveClass("text-amber-700");
  });

  it("bands a PSI at or below VR-DST-1's warn threshold as stable", () => {
    render(ColumnDrift, { props: { drift: { ...MEASURED, psi: 0.02 } } });
    expect(screen.getByText(/PSI 0\.020/)).toHaveClass("text-emerald-700");
  });

  it("does not band a PSI that was never measured", () => {
    // The defect `01` §5.3's note recorded: an unmeasured PSI rendered as a calm band.
    // It must read as absent, and carry no band colour at all.
    const { container } = render(ColumnDrift, {
      props: { drift: { ...MEASURED, psi: null } },
    });
    expect(screen.getByText(/not measured/)).toBeInTheDocument();
    expect(container.innerHTML).not.toContain("text-amber-700");
    expect(container.innerHTML).not.toContain("text-red-700");
    expect(container.innerHTML).not.toContain("text-emerald-700");
  });

  it("reports the level changes and the null-rate shift", () => {
    render(ColumnDrift, { props: { drift: MEASURED } });
    expect(screen.getByText(/\+1 new/)).toBeInTheDocument();
    expect(screen.getByText(/1 vanished/)).toBeInTheDocument();
    // A rate shift is percentage **points**, signed — 0.012 is +1.20pp, not 1.2%.
    expect(screen.getByText(/\+1\.20pp nulls/)).toBeInTheDocument();
  });

  it("omits a shift that did not happen", () => {
    render(ColumnDrift, {
      props: {
        drift: {
          column: "x",
          psi: 0.02,
          mean_shift: null,
          null_rate_shift: 0,
          new_levels: [],
          vanished_levels: [],
        },
      },
    });
    expect(screen.queryByText(/nulls/)).not.toBeInTheDocument();
    expect(screen.queryByText(/new/)).not.toBeInTheDocument();
  });
});
