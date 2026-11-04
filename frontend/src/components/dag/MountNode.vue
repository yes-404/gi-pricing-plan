<script setup lang="ts">
/**
 * A pinned sub-graph mount as one collapsed node (RL-1835 (i) 2, 4; (ii) 3). The purpose badge is
 * text, the dashed border an addition to it (NFR-463). The fragment's steps are not drawn.
 */
import { Handle, Position } from "@vue-flow/core";
import { computed } from "vue";

import type { ValidationIssue } from "@/api/ratingAlgorithms";
import type { SubGraphRef } from "@/api/subGraphs";

import { isPurposeMount, parseRef } from "./graph";

const props = defineProps<{
  data: {
    mount: SubGraphRef;
    issues: ValidationIssue[];
    diffMark?: "added" | "changed" | null;
    pinned: boolean;
  };
}>();

const mount = computed(() => props.data.mount);
const issues = computed(() => props.data.issues);
const target = computed(() => {
  const { slug, version } = parseRef(mount.value.ref);
  return `${slug}@${version}`;
});
const conditional = computed(() => isPurposeMount(mount.value));
const badge = computed(() => {
  const purposes = mount.value.purposes ?? [];
  const mta = purposes.includes("mid_term_adjustment");
  const cancellation = purposes.includes("cancellation");
  if (mta && cancellation) return "MTA + cancellation";
  return mta ? "MTA only" : "Cancellation only";
});
const label = computed(() => {
  const base = `sub-graph mount ${mount.value.mount_point} of ${target.value}`;
  const n = issues.value.length;
  return n === 0 ? base : `${base}, ${n} ${n === 1 ? "issue" : "issues"}`;
});
</script>

<template>
  <div
    role="group"
    class="rounded-md border bg-white px-3 py-2 text-sm shadow-sm"
    :class="[
      issues.length > 0 ? 'invalid border-2 border-red-700' : 'border-slate-300',
      conditional ? 'border-dashed' : '',
    ]"
    :aria-label="label"
  >
    <Handle
      type="target"
      :position="Position.Left"
      :connectable="false"
    />
    <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">
      sub-graph
    </p>
    <p class="font-medium text-slate-900">
      {{ target }}
      <span
        v-if="data.diffMark"
        class="ml-1 rounded border border-slate-700 px-1 text-xs font-semibold text-slate-900"
      >{{ data.diffMark }}</span>
    </p>
    <p class="font-mono text-xs text-slate-500">
      {{ mount.mount_point }}
    </p>
    <p
      v-if="conditional"
      class="mt-1 inline-block rounded border border-slate-700 px-1 text-xs font-semibold text-slate-900"
    >
      {{ badge }}
    </p>
    <p
      v-if="!data.pinned"
      class="mt-1 text-xs font-semibold text-amber-900"
    >
      <span aria-hidden="true">⚠</span> not pinned by this Rating Version
    </p>
    <template v-if="issues.length > 0">
      <p class="mt-1 text-xs font-semibold text-red-800">
        <span aria-hidden="true">⚠</span> {{ issues.length }}
      </p>
      <ul class="list-disc pl-4 text-xs text-red-900">
        <li
          v-for="(issue, i) in issues"
          :key="`${issue.code}-${i}`"
        >
          {{ issue.message }}
        </li>
      </ul>
    </template>
    <Handle
      type="source"
      :position="Position.Right"
      :connectable="false"
    />
  </div>
</template>
