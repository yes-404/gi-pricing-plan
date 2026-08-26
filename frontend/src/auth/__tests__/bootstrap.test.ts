import { beforeEach, describe, expect, it, vi } from "vitest";

// vi.mock factories are hoisted above this file's own top-level code, so a plain `const
// mocks` here would be in the temporal dead zone when the factory runs. vi.hoisted is
// the documented pattern for exactly this — the plan's sample was written for an older
// vitest hoisting behaviour.
const mocks = vi.hoisted(() => ({
  completeRedirectIfPresent: vi.fn(async () => null),
  initSession: vi.fn(async () => null),
}));
vi.mock("../session", () => mocks);

import { bootstrap } from "../bootstrap";

describe("the auth bootstrap", () => {
  beforeEach(() => vi.clearAllMocks());

  it("processes a redirect callback, then initializes", async () => {
    await bootstrap();
    expect(mocks.completeRedirectIfPresent).toHaveBeenCalled();
    expect(mocks.initSession).toHaveBeenCalled();
  });

  it("continues to boot anonymous when the bootstrap fails", async () => {
    mocks.initSession.mockRejectedValueOnce(new Error("config refused"));
    await expect(bootstrap()).resolves.toBeUndefined();
  });
});
