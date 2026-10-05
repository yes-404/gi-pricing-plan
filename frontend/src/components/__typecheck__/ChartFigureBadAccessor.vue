<script setup lang="ts">
/**
 * Type-check fixture, never rendered (RL-1307 §Acceptance): an accessor that reads a field the
 * row type does not have. Expected error: TS2339, Property 'bnad' does not exist on type 'Band'.
 * If the directive below ever stops being needed, `pnpm --dir frontend type-check` fails
 * with TS2578, which means the generic API has stopped checking accessors.
 */
import ChartFigure from "@/components/ChartFigure.vue";

interface Band {
  band: string;
  exposure: number;
}
const rows: Band[] = [{ band: "A", exposure: 1.5 }];
</script>

<template>
  <!-- eslint-disable vue/max-attributes-per-line -- the expect-error directive covers one line only -->
  <!-- @vue-expect-error TS2339: the accessor reads a field Band does not have -->
  <ChartFigure title="t" :rows="rows" :columns="[{ key: 'band', label: 'Band', value: (r) => r.bnad }]" />
</template>
