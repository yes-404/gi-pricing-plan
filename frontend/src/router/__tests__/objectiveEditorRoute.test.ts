import { describe, expect, it } from "vitest";
import { createMemoryHistory, createRouter } from "vue-router";

import { routes } from "../index";

// SL-1275 (WK-690 Slice 5): the authoring view is reachable at `/objectives/new`, beside the
// library (`02` §5.3). A static segment outranks the dynamic `/objectives/:id/certificate`
// from either position (index.test.ts), so this asserts resolution, not declaration order.
function matchedNames(path: string): string[] {
  return createRouter({ history: createMemoryHistory(), routes })
    .resolve(path)
    .matched.map((record) => record.name as string);
}

describe("the objective editor route", () => {
  it("resolves /objectives/new to the editor", () => {
    expect(matchedNames("/objectives/new")).toContain("objective-editor");
  });

  it("does not disturb the library or the certificate routes", () => {
    expect(matchedNames("/objectives")).toContain("objective-library");
    expect(matchedNames("/objectives/a1/certificate")).toContain("objective-certificate");
  });

  it("requires authentication, like every other objective route", () => {
    const record = routes.find((route) => route.name === "objective-editor");
    expect(record?.meta?.requiresAuth).toBe(true);
  });
});
