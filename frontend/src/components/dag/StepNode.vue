<script setup lang="ts">
// SPIKE F2: one typed custom node, registered under each of the seven 03 §3.2 step types.
import { Handle, Position, type NodeProps } from "@vue-flow/core";
import { computed } from "vue";

import type { RatingStepSpike } from "./graph";

const props = defineProps<NodeProps<RatingStepSpike>>();
const inputSlots = computed(() =>
  props.data.type === "input" ? 0 : props.data.consumes.length + 1,
);
const hasOutput = computed(() => props.data.produces !== null);
</script>

<template>
  <div class="step" :class="`step--${data.type}`" :aria-label="`${data.type} step ${data.label}`">
    <Handle
      v-for="h in inputSlots"
      :id="`in${h - 1}`"
      :key="h"
      type="target"
      :position="Position.Left"
      :style="{ top: `${(h * 100) / (inputSlots + 1)}%` }"
    />
    <span class="step__type">{{ data.type }}</span>
    <span class="step__label">{{ data.label }}</span>
    <Handle v-if="hasOutput" id="out" type="source" :position="Position.Right" />
  </div>
</template>

<style scoped>
.step { padding: 6px 10px; border: 1px solid #64748b; border-radius: 6px; background: #fff; font-size: 12px; min-width: 140px; }
.step__type { display: block; font-weight: 600; text-transform: uppercase; font-size: 10px; }
.step--input { border-color: #0284c7; }
.step--lookup { border-color: #7c3aed; }
.step--table { border-color: #16a34a; }
.step--expression { border-color: #ca8a04; }
.step--model_call { border-color: #db2777; }
.step--constraint { border-color: #dc2626; }
.step--output { border-color: #0f172a; }
</style>
