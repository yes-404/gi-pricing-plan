<script setup lang="ts">
/**
 * Type-check fixture, never rendered (RL-1307 §Acceptance): an accessor that returns a value
 * that is not a cell. Expected error: TS2322, Type 'string[]' is not assignable to type 'Cell'.
 */
import ChartFigure from "@/components/ChartFigure.vue";

interface Band {
  band: string;
  tags: string[];
}
const rows: Band[] = [{ band: "A", tags: [] }];
</script>

<template>
  <!-- eslint-disable vue/max-attributes-per-line -- the expect-error directive covers one line only -->
  <!-- @vue-expect-error TS2322: string[] is not a Cell -->
  <ChartFigure title="t" :rows="rows" :columns="[{ key: 'tags', label: 'Tags', value: (r) => r.tags }]" />
</template>
