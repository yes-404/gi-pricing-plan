import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

import { REPO_ROOT } from "../../router/__tests__/routeGraph";

// SL-1547 prep: `POST …/import` is typed 200 `ImportPreview` / 201 `RateTableVersion` in the
// contract (SL-1683), so the client must not carry a hand-composed copy of either shape.
const SOURCE = readFileSync(`${REPO_ROOT}/frontend/src/api/rateTables.ts`, "utf8");

describe("rateTables import types come from the generated contract", () => {
  it("declares no hand-written ImportPreview interface", () => {
    expect(SOURCE).not.toMatch(/interface\s+ImportPreview\b/);
  });

  it("aliases ImportPreview to the generated schema", () => {
    expect(SOURCE).toMatch(/type\s+ImportPreview\s*=\s*components\["schemas"\]\["ImportPreview"\]/);
  });

  it("no longer cites the untyped-200 hold", () => {
    expect(SOURCE).not.toContain("UNTYPED_2XX_PENDING_PART_B");
  });
});
