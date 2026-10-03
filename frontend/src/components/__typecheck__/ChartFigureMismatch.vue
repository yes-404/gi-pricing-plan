<script setup lang="ts">
/**
 * Type-check fixture, never rendered (RL-1307 §Acceptance): columns written for one row type
 * passed with rows of another. Expected error: TS2322, Type 'Band[]' is not assignable to
 * type 'readonly Other[]'.
 */
import type { Column } from "@/chart-table";
import ChartFigure from "@/components/ChartFigure.vue";

interface Band {
  band: string;
}
interface Other {
  level: number;
}
const rows: Band[] = [{ band: "A" }];
const columns: Column<Other>[] = [{ key: "level", label: "Level", value: (o) => o.level }];
</script>

<template>
  <!-- eslint-disable vue/max-attributes-per-line -- the expect-error directive covers one line only -->
  <!-- @vue-expect-error TS2322: columns for Other, rows of Band -->
  <ChartFigure title="t" :rows="rows" :columns="columns" />
</template>
