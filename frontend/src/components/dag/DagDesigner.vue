<script setup lang="ts">
// SPIKE F2: the canvas. State lives in Vue Flow's store; validation is the pure checkConnection.
import "@vue-flow/core/dist/style.css";
import "@vue-flow/core/dist/theme-default.css";

import { type Connection, type Edge, VueFlow, useVueFlow } from "@vue-flow/core";
import { markRaw, shallowRef } from "vue";

import { STEP_TYPES, type StepNode, checkConnection } from "./graph";
import StepNodeView from "./StepNode.vue";

const props = defineProps<{ nodes: StepNode[]; edges: Edge[] }>();

const nodeTypes = markRaw(Object.fromEntries(STEP_TYPES.map((t) => [t, StepNodeView])));
const { getNodes, getEdges, addEdges, onConnect, setViewport } = useVueFlow();
// Spike measurement hook (dev only): a programmatic viewport transition for the fps probe.
if (import.meta.env.DEV) (window as unknown as { __f2SetViewport?: typeof setViewport }).__f2SetViewport = setViewport;
const lastRejection = shallowRef<string | null>(null);

function isValidConnection(c: Connection): boolean {
  const t0 = performance.now();
  const r = checkConnection(c, getNodes.value as StepNode[], getEdges.value);
  const w = window as unknown as { __f2Timings?: number[] };
  (w.__f2Timings ??= []).push(performance.now() - t0);
  lastRejection.value = r;
  return r === null;
}
onConnect((c) => addEdges([c]));
</script>

<template>
  <div class="designer">
    <VueFlow
      :nodes="props.nodes"
      :edges="props.edges"
      :node-types="nodeTypes"
      :is-valid-connection="isValidConnection"
      :delete-key-code="['Delete', 'Backspace']"
      :min-zoom="0.05"
      :only-render-visible-elements="false"
      fit-view-on-init
    />
    <p class="designer__status" role="status">{{ lastRejection ?? "ok" }}</p>
  </div>
</template>

<style scoped>
.designer { position: relative; width: 100%; height: 100vh; }
.designer__status { position: absolute; bottom: 4px; left: 4px; margin: 0; font-size: 12px; }
</style>
