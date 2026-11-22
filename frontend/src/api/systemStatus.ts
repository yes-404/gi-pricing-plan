import { request } from "./client";
import type { components } from "./generated/schema";

export type SystemStatus = components["schemas"]["SystemStatus"];

/** `GET /admin/status`: deployment-wide health, queues, blob usage and cache counts (07 §4.6). */
export function getSystemStatus(): Promise<SystemStatus> {
  return request<SystemStatus>("/admin/status");
}
