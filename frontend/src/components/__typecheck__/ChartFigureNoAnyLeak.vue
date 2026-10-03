<script setup lang="ts">
/**
 * Type-check fixture, never rendered (RL-1307's spike, beyond its four acceptance checks): the
 * accessor's parameter is inferred as the row type, not `any`. `r.band` is a string, so
 * assigning it to a number must fail. Expected error: TS2322, Type 'string' is not assignable
 * to type 'number'. If `T` ever widened to `any`, this directive would go unused and the
 * type-check would fail with TS2578.
 */
import ChartFigure from "@/components/ChartFigure.vue";

interface Band {
  band: string;
}
const rows: Band[] = [{ band: "A" }];
</script>

<template>
  <!-- eslint-disable vue/max-attributes-per-line -- the expect-error directive covers one line only -->
  <!-- @vue-expect-error TS2322: r is Band, so r.band is a string -->
  <ChartFigure title="t" :rows="rows" :columns="[{ key: 'x', label: 'X', value: (r) => { const n: number = r.band; return n; } }]" />
</template>
