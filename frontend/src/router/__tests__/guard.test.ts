import { beforeEach, describe, expect, it, vi } from "vitest";

// vi.mock factories are hoisted above this file's own top-level code, so a plain `const
// mocks` here would be in the temporal dead zone when the factory runs. vi.hoisted is
// the documented pattern for exactly this — the plan's sample was written for an older
// vitest hoisting behaviour.
const mocks = vi.hoisted(() => ({ isSignedIn: vi.fn(), signIn: vi.fn(async () => {}) }));
vi.mock("../../auth/session", () => mocks);

import { router } from "../index";

beforeEach(() => {
  vi.clearAllMocks();
});

describe("the auth guard", () => {
  // The anonymous case first: the guard's `return false` cancels the navigation, so the
  // router stays at `/` and the signed-in test's push below is a fresh navigation. In
  // the plan's order the signed-in push left the router at `/data`, and pushing the same
  // path again is a duplicate navigation — vue-router's `navigate` short-circuits it
  // before the guard queue, so the sign-in call never happened.
  it("redirects an anonymous visitor to the provider via signIn", async () => {
    mocks.isSignedIn.mockReturnValue(false);
    await router.push("/data");
    expect(mocks.signIn).toHaveBeenCalled();
  });

  it("lets a signed-in user through", async () => {
    mocks.isSignedIn.mockReturnValue(true);
    await router.push("/data");
    expect(mocks.signIn).not.toHaveBeenCalled();
    expect(router.currentRoute.value.path).toBe("/data");
  });
});
