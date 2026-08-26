import { readonly, ref } from "vue";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/vue";
import userEvent from "@testing-library/user-event";

// vi.mock factories are hoisted above this file's own top-level code, so a plain `const
// mocks` here would be in the temporal dead zone when the factory runs. The ref itself
// must be built inside the factory (only `vi` survives hoisting), so the holder carries
// the value the factory snapshots when each component setup calls useSessionUser — the
// tests set it before render, exactly as the plan's sample set `user.value`.
const state = vi.hoisted(() => ({
  user: null as { profile?: { name?: string } } | null,
}));
const mocks = vi.hoisted(() => ({
  signIn: vi.fn(async () => {}),
  signOut: vi.fn(async () => {}),
}));
vi.mock("../../auth/session", () => ({
  useSessionUser: () => readonly(ref(state.user)),
  signIn: mocks.signIn,
  signOut: mocks.signOut,
}));

import AuthControl from "../AuthControl.vue";

describe("the auth control", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    state.user = null;
  });

  it("shows Sign in when anonymous and calls signIn on click", async () => {
    render(AuthControl);
    await userEvent.click(screen.getByRole("button", { name: "Sign in" }));
    expect(mocks.signIn).toHaveBeenCalled();
  });

  it("shows the user's name and Sign out when signed in, calling signOut on click", async () => {
    state.user = { profile: { name: "A. Analyst" } };
    render(AuthControl);
    expect(screen.getByText("A. Analyst")).toBeTruthy();
    await userEvent.click(screen.getByRole("button", { name: "Sign out" }));
    expect(mocks.signOut).toHaveBeenCalled();
  });
});
