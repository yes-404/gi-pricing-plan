<script setup lang="ts">
import { Handle, Position } from "@vue-flow/core";
import { computed } from "vue";

import type { RatingStep } from "@/api/ratingAlgorithms";

import { names } from "./graph";

const props = defineProps<{ data: { step: RatingStep } }>();

const step = computed(() => props.data.step);
</script>

<template>
  <div
    class="rounded-md border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm"
    :aria-label="`${step.type} step ${step.label} (${step.step_id})`"
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
    <Handle
      type="source"
      :position="Position.Right"
      :connectable="false"
    />
  </div>
</template>
