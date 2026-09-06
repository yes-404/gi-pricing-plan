import { describe, expect, it } from "vitest";

import { bandOf, blocksModelling, groupIntoBands, type RuleResult, type ValidationReport } from "../validation";

function rule(over: Partial<RuleResult> & Pick<RuleResult, "outcome">): RuleResult {
  return {
    rule_id: crypto.randomUUID(),
    rule_slug: "a-rule",
    rule_version: 1,
    layer: "structural",
    severity: "fail",
    measured: {},
    threshold: {},
    detail: "",
    offending_sample: [],
    ...over,
  } as RuleResult;
}

function report(...results: RuleResult[]): ValidationReport {
  return {
    id: crypto.randomUUID(),
    dataset_version_id: crypto.randomUUID(),
    rule_set_id: crypto.randomUUID(),
    rule_set_version: 1,
    started_at: "2026-08-15T09:00:00Z",
    finished_at: "2026-08-15T09:00:01Z",
    results,
    empty_layers: [],
  } as ValidationReport;
}

const ACK = { user_id: crypto.randomUUID(), at: "2026-08-15T09:05:00Z", justification: "ok" };

describe("banding, which decides what a reader sees first", () => {
  it("puts fails and errors together, because both block equally", () => {
    // An `error` means the rule did not run. FR-48 makes that never a pass, and a
    // reader asking "why can I not fit a model on this?" must see it beside the failures.
    expect(bandOf(rule({ outcome: "fail" }))).toBe("blocking");
    expect(bandOf(rule({ outcome: "error" }))).toBe("blocking");
  });

  it("separates warnings that need an actuary from ones that have had one", () => {
    expect(bandOf(rule({ outcome: "warn" }))).toBe("needs-acknowledgement");
    expect(bandOf(rule({ outcome: "warn", acknowledgement: ACK }))).toBe("acknowledged");
  });

  it("leaves passes and skips out of the way", () => {
    expect(bandOf(rule({ outcome: "pass" }))).toBe("other");
    expect(bandOf(rule({ outcome: "skipped" }))).toBe("other");
  });
});

describe("what the banner is allowed to claim", () => {
  it("blocks while anything failed", () => {
    expect(blocksModelling(report(rule({ outcome: "fail" }), rule({ outcome: "pass" })))).toBe(true);
  });

  it("blocks while a warning is unacknowledged — the state the count alone cannot show", () => {
    expect(blocksModelling(report(rule({ outcome: "warn" })))).toBe(true);
  });

  it("clears once every warning is acknowledged and nothing failed", () => {
    // The same two facts `promote_to_validated` uses, so the banner cannot say a version
    // is ready when the platform would refuse it.
    expect(
      blocksModelling(report(rule({ outcome: "warn", acknowledgement: ACK }), rule({ outcome: "pass" }))),
    ).toBe(false);
  });

  it("counts an empty report as clear", () => {
    expect(blocksModelling(report())).toBe(false);
  });
});

describe("grouping", () => {
  it("keeps every result in exactly one band", () => {
    const results = [
      rule({ outcome: "fail" }),
      rule({ outcome: "error" }),
      rule({ outcome: "warn" }),
      rule({ outcome: "warn", acknowledgement: ACK }),
      rule({ outcome: "pass" }),
      rule({ outcome: "skipped" }),
    ];
    const bands = groupIntoBands(report(...results));
    const total = Object.values(bands).reduce((sum, band) => sum + band.length, 0);
    expect(total).toBe(results.length);
    expect(bands.blocking).toHaveLength(2);
    expect(bands["needs-acknowledgement"]).toHaveLength(1);
    expect(bands.acknowledged).toHaveLength(1);
    expect(bands.other).toHaveLength(2);
  });
});
