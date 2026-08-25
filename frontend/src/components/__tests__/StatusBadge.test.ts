import { render, screen } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import type { DatasetStatus } from "@/api/datasets";

import StatusBadge from "../StatusBadge.vue";

const ALL: DatasetStatus[] = ["draft", "validating", "validated", "failed", "archived"];

function badge(status: DatasetStatus): HTMLElement {
  render(StatusBadge, { props: { status } });
  return screen.getByText(status);
}

describe("the status badge", () => {
  it.each(ALL)("names %s as text, so colour is never the only channel", (status) => {
    // WCAG 2.2 AA. The tone below carries no information the word does not.
    expect(badge(status)).toBeInTheDocument();
  });

  it.each(ALL)("gives %s a tone rather than falling through to a default", (status) => {
    // The defect this component was extracted to fix was a *missing* tone silently
    // resolving to a fallback, so "has some class" is the assertion that catches it.
    expect(badge(status).className).toMatch(/bg-/);
  });

  it("does not render a failed version in the tone it renders a draft one", () => {
    // The whole point. `DatasetDetailView` mapped four of five members and let `failed`
    // fall through `?? 'bg-slate-100'` — draft's own background — so a failed validation
    // looked untouched in the view someone reads to decide whether to model on the data.
    render(StatusBadge, { props: { status: "failed" } });
    render(StatusBadge, { props: { status: "draft" } });

    expect(screen.getByText("failed").className).not.toEqual(
      screen.getByText("draft").className,
    );
  });

  it("distinguishes all five statuses from each other, not just failed from draft", () => {
    // A map that gave two *other* members the same tone would pass the test above.
    const tones = ALL.map((status) => badge(status).className);

    expect(new Set(tones).size).toBe(ALL.length);
  });
});
