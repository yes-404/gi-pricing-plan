import { describe, expect, it } from "vitest";

import { psiBand } from "@/api/profiles";

describe("psiBand", () => {
  it("bands against the rule's own warn_above, not a literal", () => {
    // 0.15 is above VR-DST-1's 0.10 default but below the 0.25 this function used to invent.
    // Under two bands it is "shifted"; the third band it used to return asserted a `fail`
    // severity VR-DST-1 cannot emit (`01:996`).
    expect(psiBand(0.15, 0.1)).toBe("shifted");
    expect(psiBand(0.05, 0.1)).toBe("stable");
    // A workspace that versioned VR-DST-1 to a tighter threshold gets its own answer.
    expect(psiBand(0.05, 0.02)).toBe("shifted");
  });
});
