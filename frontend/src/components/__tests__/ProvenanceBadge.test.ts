import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import ProvenanceBadge from "@/components/ProvenanceBadge.vue";
import { BACKTEST, COMPARISON, DIAGNOSTICS } from "@/views/__tests__/fixtures";

// Any RouterLink the badge rendered would become an `<a>` here, so "no link" is asserted
// against both a plain anchor and a router link (#1869 (a): no Jobs view exists to link to).
const global = {
  stubs: { RouterLink: { props: ["to"], template: "<a :href='to'><slot /></a>" } },
};

function badge(): HTMLElement {
  return screen.getByRole("group", { name: "Provenance" });
}

describe("ProvenanceBadge (FR-2159)", () => {
  it("shows the producing Job's id as text, with no link to it", () => {
    const { container } = render(ProvenanceBadge, {
      props: { provenance: DIAGNOSTICS.provenance },
      global,
    });
    const jobId = DIAGNOSTICS.provenance.produced_by_job_id;
    expect(jobId).not.toBeNull();
    expect(within(badge()).getByText(jobId!)).toBeInTheDocument();
    // #1869 (a): the id is text until the Work that builds `/jobs` adds the link.
    expect(screen.queryByRole("link")).toBeNull();
    expect(container.querySelector("a, [href]")).toBeNull();
    expect(within(badge()).queryByText(/not recorded/i)).toBeNull();
  });

  it('says "not recorded" for a null producing Job, never a blank', () => {
    expect(BACKTEST.provenance.produced_by_job_id).toBeNull();
    const { container } = render(ProvenanceBadge, {
      props: { provenance: BACKTEST.provenance },
      global,
    });
    const job = within(badge()).getByText("not recorded");
    expect(job).toBeInTheDocument();
    // The "not recorded" sits in the Job's own slot, not somewhere else in the badge.
    expect(job.closest("div")).toHaveTextContent(/Produced by Job\s*not recorded/);
    expect(container.querySelector("a, [href]")).toBeNull();
  });

  it("names the artifact itself: its type and its id", () => {
    render(ProvenanceBadge, { props: { provenance: DIAGNOSTICS.provenance }, global });
    expect(badge()).toHaveTextContent("Diagnostics");
    expect(within(badge()).getByText(DIAGNOSTICS.provenance.entity_id)).toBeInTheDocument();
  });

  it("says in words that a governed parent could not be written as a reference, never a blank", () => {
    // FR-2159's amendment of 2026-11-21 (ADR-2170): a parent whose stored ref cannot be read.
    const provenance = { ...DIAGNOSTICS.provenance, subject_refs: [], unnamed_subjects: 1 };
    render(ProvenanceBadge, { props: { provenance }, global });
    expect(badge()).toHaveTextContent(
      /About\s*1 governed parent could not be written as a reference/,
    );
  });

  it("lists the parents it can name and counts the ones it cannot", () => {
    const provenance = { ...COMPARISON.provenance, unnamed_subjects: 2 };
    render(ProvenanceBadge, { props: { provenance }, global });
    for (const ref of COMPARISON.provenance.subject_refs) {
      expect(badge()).toHaveTextContent(ref);
    }
    expect(badge()).toHaveTextContent("2 governed parents could not be written as a reference");
  });

  it("shows every subject ref, in the order the object gives them", () => {
    // ModelComparison carries two: FR-2159 orders them as `summary.model_refs`.
    render(ProvenanceBadge, { props: { provenance: COMPARISON.provenance }, global });
    const refs = COMPARISON.provenance.subject_refs;
    expect(refs.length).toBeGreaterThan(1);
    const text = badge().textContent ?? "";
    const positions = refs.map((ref) => text.indexOf(ref));
    expect(positions.every((p) => p >= 0)).toBe(true);
    expect([...positions].sort((a, b) => a - b)).toEqual(positions);
  });
});
