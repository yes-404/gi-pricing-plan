<script setup lang="ts">
import DagDesigner from "@/components/dag/DagDesigner.vue";
import { buildStructure } from "@/components/dag/graph";

const { nodes, edges } = buildStructure(200);
</script>

<template>
  <DagDesigner :nodes="nodes" :edges="edges" />
</template>
