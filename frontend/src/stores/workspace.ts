import { defineStore } from "pinia";

import { setWorkspaceId } from "../api/client";
import { listWorkspaces, switchWorkspace, type WorkspaceMembership } from "../api/me";

/** Per-tab, survives a reload, never shared across tabs (sessionStorage): two tabs may
 *  hold two workspaces — the case FR-PLAT-65's per-request transport exists for — and a
 *  reload restores the selection without a new POST, which is correct under OQ-PLAT-12:
 *  a switch is a human act, and a reload is not one. */
const STORAGE_KEY = "gi.workspaceId";

export const useWorkspaceStore = defineStore("workspace", {
  state: () => ({
    workspaces: [] as WorkspaceMembership[],
    current: null as WorkspaceMembership | null,
  }),
  getters: {
    needsSelection: (state) => state.workspaces.length > 1,
  },
  actions: {
    async load() {
      this.workspaces = await listWorkspaces();
      const remembered = sessionStorage.getItem(STORAGE_KEY);
      const match = remembered
        ? this.workspaces.find((w) => w.workspace_id === remembered)
        : undefined;
      const sole = this.workspaces.length === 1 ? (this.workspaces[0] ?? null) : null;
      this.current = match ?? sole;
      setWorkspaceId(this.current?.workspace_id ?? null);
    },
    async select(workspaceId: string) {
      const entered = await switchWorkspace(workspaceId);
      this.current = entered;
      sessionStorage.setItem(STORAGE_KEY, entered.workspace_id);
      setWorkspaceId(entered.workspace_id);
      // Views hold workspace-scoped data; a reload re-fetches under the new header.
      window.location.reload();
    },
  },
});
