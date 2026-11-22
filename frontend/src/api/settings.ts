import { request } from "./client";
import type { components } from "./generated/schema";

export type SettingResolution = components["schemas"]["SettingResolution"];
export type SettingCandidate = components["schemas"]["SettingCandidate"];
export type SettingScope = components["schemas"]["SettingScope"];
export type SettingSource = components["schemas"]["SettingSource"];
export type SettingType = components["schemas"]["SettingType"];

/** `GET /settings` — every setting's resolution, needs `settings:read` (`07` §5.1, FR-446). */
export function listSettings(): Promise<SettingResolution[]> {
  return request<SettingResolution[]>("/settings");
}

/**
 * `PUT /settings` for one key.
 *
 * One request per edited key, so a refusal belongs to exactly one row. The response is the
 * whole list, resolved again. Needs `admin:manage_settings`. The route sets a workspace
 * value; no route removes one.
 */
export function updateSetting(key: string, value: unknown): Promise<SettingResolution[]> {
  return request<SettingResolution[]>("/settings", {
    method: "PUT",
    body: { values: { [key]: value } },
  });
}
