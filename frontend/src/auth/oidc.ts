import {
  InMemoryWebStorage,
  Log,
  UserManager,
  WebStorageStateStore,
  type User,
} from "oidc-client-ts";

import type { OidcAuthConfig } from "./config";

/** The UserManager settings FR-393's clauses imply: code+PKCE, memory-only storage,
 *  silent renewal by prompt=none iframe (the realm plan is silent on refresh tokens — Finding 4). */
export function buildManager(config: OidcAuthConfig): UserManager {
  Log.setLevel(Log.INFO);
  return new UserManager({
    authority: config.issuer,
    client_id: config.client_id,
    redirect_uri: `${window.location.origin}/callback`,
    silent_redirect_uri: `${window.location.origin}/silent-renew`,
    response_type: "code",
    scope: "openid profile email",
    // oidc-client-ts 3.5.0: InMemoryWebStorage implements Storage, not StateStore; the
    // adapter makes it the userStore while keeping FR-388's memory-only rule.
    userStore: new WebStorageStateStore({ store: new InMemoryWebStorage() }),
    automaticSilentRenew: true,
    accessTokenExpiringNotificationTimeInSeconds: 60,
  });
}

/** Process a redirect callback; no-op when the URL carries no code/state. */
export async function completeSignin(manager: UserManager): Promise<User | null> {
  if (!new URLSearchParams(window.location.search).has("code")) return null;
  const user = await manager.signinRedirectCallback();
  window.history.replaceState({}, "", window.location.pathname);
  return user;
}
