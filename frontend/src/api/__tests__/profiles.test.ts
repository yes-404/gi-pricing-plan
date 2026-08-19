import { describe, expect, it } from "vitest";

import { psiBand } from "@/api/profiles";

describe("psiBand", () => {
  // `01` §4.4's VR-DST-1: warn **above** 0.10, fail **above** 0.25. The boundaries are
  // exclusive, so a PSI landing exactly on a threshold is the calmer band — the same
  // reading the validation rule uses, because a rule's verdict and this badge must not
  // disagree about one number.
  it("bands strictly above each threshold, never on it", () => {
    expect(psiBand(0)).toBe("stable");
    expect(psiBand(0.1)).toBe("stable");
    expect(psiBand(0.1001)).toBe("shifted");
    expect(psiBand(0.25)).toBe("shifted");
    expect(psiBand(0.2501)).toBe("broken");
  });
});
