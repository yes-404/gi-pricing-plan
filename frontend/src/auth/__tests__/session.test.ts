import { beforeEach, describe, expect, it, vi } from "vitest";

const managerStub = {
  getUser: vi.fn(),
  signinRedirect: vi.fn(),
  signinRedirectCallback: vi.fn(),
  signinSilent: vi.fn(),
  signinSilentCallback: vi.fn(),
  signoutRedirect: vi.fn(),
  events: {
    addUserLoaded: vi.fn(),
    addAccessTokenExpiring: vi.fn(),
    addSilentRenewError: vi.fn(),
    addUserSignedOut: vi.fn(),
  },
};
vi.mock("oidc-client-ts", () => ({
  // vitest 4 Reflect.constructs the implementation itself, and an arrow function has no
  // [[Construct]] — the factory must be a function expression. (Plan Task 4's sample used
  // an arrow; changed.)
  UserManager: vi.fn(function () {
    return managerStub;
  }),
  // Returns nothing so `new` builds a prototype-typed instance `instanceof` accepts.
  WebStorageStateStore: vi.fn(function () {}),
  InMemoryWebStorage: vi.fn(),
  Log: { setLevel: vi.fn() },
}));
vi.mock("../../api/client", () => ({ setAccessToken: vi.fn(), clearAccessToken: vi.fn() }));
vi.mock("../config", () => ({
  loadAuthConfig: vi.fn(async () => ({
    issuer: "http://localhost:8080/realms/gi-pricing",
    client_id: "gi-pricing-frontend",
    dev_auth_enabled: true,
  })),
}));

import { initSession, signIn, signOut } from "../session";
import { setAccessToken, clearAccessToken } from "../../api/client";
import { UserManager, InMemoryWebStorage, WebStorageStateStore } from "oidc-client-ts";

beforeEach(() => {
  vi.clearAllMocks();
});

describe("the auth session", () => {
  it("builds the manager from the config with memory-only storage", async () => {
    await initSession();
    const settings = vi.mocked(UserManager).mock.calls[0]![0];
    expect(settings).toMatchObject({
      authority: "http://localhost:8080/realms/gi-pricing",
      client_id: "gi-pricing-frontend",
      response_type: "code",
      automaticSilentRenew: true,
    });
    // FR-PLAT-2: the state store is the adapter over InMemoryWebStorage — never
    // localStorage. `WebStorageStateStore`'s first-call argument carries the store.
    expect(settings.userStore).toBeInstanceOf(WebStorageStateStore);
    const storeOpts = vi.mocked(WebStorageStateStore).mock.calls[0]![0];
    expect(storeOpts?.store).toBeInstanceOf(InMemoryWebStorage);
  });

  it("pushes the bearer token into the api client on user load, clears on unload", async () => {
    await initSession();
    const onLoaded = vi.mocked(managerStub.events.addUserLoaded).mock.calls[0]![0];
    const onSignedOut = vi.mocked(managerStub.events.addUserSignedOut).mock.calls[0]![0];
    onLoaded({ access_token: "t" });
    expect(setAccessToken).toHaveBeenCalledWith("t");
    onSignedOut();
    expect(clearAccessToken).toHaveBeenCalled();
  });

  it("renews silently when the token approaches expiry, and logs out when renewal fails", async () => {
    await initSession();
    const onExpiring = vi.mocked(managerStub.events.addAccessTokenExpiring).mock.calls[0]![0];
    const onRenewError = vi.mocked(managerStub.events.addSilentRenewError).mock.calls[0]![0];
    onExpiring();
    expect(managerStub.signinSilent).toHaveBeenCalled();
    onRenewError();
    // FR-PLAT-55's sentence: failure to renew logs the session out rather than
    // retrying indefinitely — an expired session that looks logged in is worse.
    expect(managerStub.signoutRedirect).toHaveBeenCalled();
  });

  it("signIn redirects, signOut redirects through the provider", async () => {
    await initSession();
    await signIn();
    expect(managerStub.signinRedirect).toHaveBeenCalled();
    await signOut();
    expect(managerStub.signoutRedirect).toHaveBeenCalled();
  });
});
