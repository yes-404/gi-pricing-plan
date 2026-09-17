import { request } from "./client";
import type { components } from "./generated/schema";

export type WorkspaceMembership = components["schemas"]["WorkspaceMembership"];

/** Every workspace this principal is a member of, each named. Unscoped, so a first
 *  selection can be made (07 FR-396). */
export function listWorkspaces(): Promise<WorkspaceMembership[]> {
  return request<WorkspaceMembership[]>("/me/workspaces");
}

/** Choose the workspace to act in; the platform audits the switch (07 FR-396). */
export function switchWorkspace(workspaceId: string): Promise<WorkspaceMembership> {
  return request<WorkspaceMembership>("/me/workspace", {
    method: "POST",
    body: { workspace_id: workspaceId },
  });
}
