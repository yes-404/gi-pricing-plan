import { request } from "../api/client";
import type { components } from "../api/generated/schema";

export type OidcAuthConfig = components["schemas"]["OidcAuthConfig"];

let cached: OidcAuthConfig | null = null;

/** The issuer and client_id the PKCE flow cannot start without (07 FR-PLAT-66).
 *  Fetched once per page load; the values are public by design. */
export async function loadAuthConfig(): Promise<OidcAuthConfig> {
  cached ??= await request<OidcAuthConfig>("/auth/config");
  return cached;
}
