import { readonly, ref } from "vue";
import type { User, UserManager } from "oidc-client-ts";

import { clearAccessToken, setAccessToken } from "../api/client";
import { loadAuthConfig } from "./config";
import { buildManager, completeSignin } from "./oidc";

/** The session is in memory only (FR-388, load-bearing per OQ-644): a hard reload
 *  clears it, and the boot sequence (Task 6) restores it through a silent provider check —
 *  an act of the provider session, not of storage. A module singleton, not a Pinia store:
 *  the filed W6b-11 plan owns the app's first store (Finding 5). */
export let currentUser: User | null = null;

const userRef = ref<User | null>(null);

/** Reactive view of the session for rendering; `currentUser` is the guard's plain read. */
export function useSessionUser() {
  return readonly(userRef);
}

export const isSignedIn = (): boolean => currentUser !== null;

let manager: UserManager | null = null;

function adopt(user: User | null): void {
  currentUser = user;
  userRef.value = user;
  if (user) setAccessToken(user.access_token);
  else clearAccessToken();
}

export async function initSession(): Promise<User | null> {
  manager = buildManager(await loadAuthConfig());
  manager.events.addUserLoaded((user) => adopt(user));
  manager.events.addUserSignedOut(() => adopt(null));
  manager.events.addAccessTokenExpiring(() => {
    // FR-393: renewal is silent; a hard reload alone would look logged-out.
    void manager?.signinSilent();
  });
  manager.events.addSilentRenewError(() => {
    // An expired session that looks logged in is how a user comes to believe the
    // platform lost their work — so failure logs out (FR-393's sentence).
    void manager?.signoutRedirect();
  });
  const user = await manager.getUser();
  if (user) adopt(user);
  return user;
}

export async function signIn(): Promise<void> {
  await manager?.signinRedirect();
}

export async function signOut(): Promise<void> {
  await manager?.signoutRedirect();
}

export async function completeRedirectIfPresent(): Promise<User | null> {
  return manager ? completeSignin(manager) : null;
}

export async function completeSilentRenew(): Promise<void> {
  if (!manager) return;
  await manager.signinSilentCallback();
}
