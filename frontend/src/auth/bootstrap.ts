import { completeRedirectIfPresent, initSession } from "./session";

/** Runs once before the app mounts: finish a redirect the provider just sent us,
 *  then establish the session (memory-only; the silent provider check restores it). */
export async function bootstrap(): Promise<void> {
  try {
    await completeRedirectIfPresent();
    await initSession();
  } catch (error) {
    // A failed bootstrap (the platform is down, the config fetch refused) must not leave
    // a blank page: mount anonymous, and the guard's sign-in attempt fails loudly at the
    // provider rather than silently here.
    console.error("auth bootstrap failed; continuing without a session", error);
  }
}
