<script setup lang="ts">
import { onMounted } from "vue";

import { useWorkspaceStore } from "@/stores/workspace";

const store = useWorkspaceStore();
onMounted(() => store.load());
</script>

<template>
  <div
    v-if="store.workspaces.length"
    class="flex items-center gap-2 text-sm"
    data-testid="workspace-selector"
  >
    <span
      v-if="store.current"
      class="text-slate-500"
    >{{ store.current.name }}</span>
    <select
      v-if="store.needsSelection"
      :value="store.current?.workspace_id ?? ''"
      aria-label="Workspace"
      class="rounded border border-slate-300 bg-white px-2 py-1"
      data-testid="workspace-select"
      @change="store.select(($event.target as HTMLSelectElement).value)"
    >
      <option
        v-if="!store.current"
        value=""
        disabled
      >
        Choose a workspace…
      </option>
      <option
        v-for="w in store.workspaces"
        :key="w.workspace_id"
        :value="w.workspace_id"
      >
        {{ w.name }}
      </option>
    </select>
  </div>
</template>
