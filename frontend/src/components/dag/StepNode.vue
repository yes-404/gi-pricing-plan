<script setup lang="ts">
import { Handle, Position } from "@vue-flow/core";
import { computed } from "vue";

import type { RatingStep, ValidationIssue } from "@/api/ratingAlgorithms";

import { names } from "./graph";

const props = defineProps<{ data: { step: RatingStep; issues: ValidationIssue[] } }>();

const step = computed(() => props.data.step);
const issues = computed(() => props.data.issues);
const label = computed(() => {
  const base = `${step.value.type} step ${step.value.label} (${step.value.step_id})`;
  const n = issues.value.length;
  return n === 0 ? base : `${base}, ${n} ${n === 1 ? "issue" : "issues"}`;
});
</script>

<template>
  <div
    role="group"
    class="rounded-md border bg-white px-3 py-2 text-sm shadow-sm"
    :class="issues.length > 0 ? 'invalid border-2 border-red-700' : 'border-slate-300'"
    :aria-label="label"
  >
    <Handle
      type="target"
      :position="Position.Left"
      :connectable="false"
    />
    <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">
      {{ step.type }}
    </p>
    <p class="font-medium text-slate-900">
      {{ step.label }}
    </p>
    <p class="font-mono text-xs text-slate-500">
      {{ step.step_id }}
    </p>
    <p
      v-if="names(step.produces).length > 0"
      class="mt-1 text-xs text-slate-600"
    >
      → {{ names(step.produces).join(", ") }}
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
