import { describe, expect, it } from "vitest";

import type { StepChange } from "@/api/score";

import { stepChangeLabel } from "../stepChange";

// PL 8054 Task 1 (SL-1550, WK-675 lane C S7): the label a compare row carries for one
// StepChange. `own_change: false` means the definition is the same on both sides and the step
// moved only through what it consumed (03 §4.10; RL-1261).

describe("stepChangeLabel", () => {
  it("FR-262 A1: an added step reads 'Added in comparison'", () => {
    const c: StepChange = { step_id: "s_new", change: "added", own_change: true, base: null };
    expect(stepChangeLabel(c)).toBe("Added in comparison");
  });

  it("FR-262 A2: a removed step reads 'Removed in comparison'", () => {
    const c: StepChange = { step_id: "s_old", change: "removed", own_change: true, comparison: null };
    expect(stepChangeLabel(c)).toBe("Removed in comparison");
  });

  it("FR-262 A3: an edited step reads 'Edited'", () => {
    const c: StepChange = {
      step_id: "s_rate",
      change: "changed",
      own_change: true,
      changed_fields: ["produced"],
    };
    expect(stepChangeLabel(c)).toBe("Edited");
  });

  it("FR-262 A4 (PL-1286 item 8): an edited step whose input also moved names both causes", () => {
    const c: StepChange = {
      step_id: "s_total",
      change: "changed",
      own_change: true,
      changed_fields: ["consumed", "produced"],
    };
    expect(stepChangeLabel(c)).toBe("Edited; its inputs also changed");
  });

  it("FR-262 A5: own_change false reads 'Changed through its inputs'", () => {
    const c: StepChange = {
      step_id: "s_ipt",
      change: "changed",
      own_change: false,
      changed_fields: ["consumed", "produced"],
    };
    expect(stepChangeLabel(c)).toBe("Changed through its inputs");
  });

  it("FR-262 A6 (PL-1286 item 8 guard): no label for any combination says 'unchanged' or 'not edited'", () => {
    const changes: StepChange["change"][] = ["added", "removed", "changed"];
    for (const change of changes) {
      for (const own_change of [true, false]) {
        for (const withConsumed of [true, false]) {
          const c: StepChange = {
            step_id: "s_x",
            change,
            own_change,
            changed_fields: withConsumed ? ["consumed", "produced"] : ["produced"],
          };
          const label = stepChangeLabel(c);
          expect(label).not.toBe("");
          expect(label).not.toMatch(/unchanged|not edited/i);
        }
      }
    }
  });
});
