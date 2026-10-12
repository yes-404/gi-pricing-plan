import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import type { Trace } from "@/api/score";

import TraceTimeline from "../TraceTimeline.vue";

const TRACE: Trace = {
  rating_version_ref: "rating_version:motor-gb@1",
  bundle_hash: `sha256:${"b".repeat(64)}`,
  ladder_reconciled: true,
  steps: [
    { step_id: "s_in", type: "input", label: "Driver age", consumed: {}, produced: { driver_age: 34 }, elapsed_us: 12 },
    {
      step_id: "s_tbl",
      type: "table",
      label: "Age relativity",
      consumed: { driver_age: 34 },
      produced: { age_rel: "1.2" },
      matched: { age_band: "30-39" },
      elapsed_us: 40,
    },
  ],
};

describe("TraceTimeline (FR-258)", () => {
  it("lists every step in order with id, label, consumed, produced and elapsed time", () => {
    render(TraceTimeline, { props: { trace: TRACE } });
    const steps = within(screen.getByRole("list", { name: "Trace steps" })).getAllByRole("listitem");
    expect(steps).toHaveLength(2);
    expect(steps[0]).toHaveTextContent("Driver age");
    expect(steps[0]).toHaveTextContent("s_in");
    expect(steps[0]).toHaveTextContent("12 µs");
    expect(steps[1]).toHaveTextContent('{"driver_age":34}');
    expect(steps[1]).toHaveTextContent('{"age_rel":"1.2"}');
  });

  it("shows the matched table row key where a step matched one, and the bundle hash and version", () => {
    render(TraceTimeline, { props: { trace: TRACE } });
    expect(screen.getByText('{"age_band":"30-39"}')).toBeInTheDocument();
    expect(screen.getByText(TRACE.bundle_hash)).toBeInTheDocument();
    expect(screen.getByText("rating_version:motor-gb@1")).toBeInTheDocument();
  });
});
