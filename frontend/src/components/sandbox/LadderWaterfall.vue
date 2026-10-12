<script setup lang="ts">
/**
 * The Premium Ladder as a waterfall with its table (03 FR-247, FR-248, FR-252, NFR-463).
 *
 * Every rung the result carries is drawn, in the order the result gives them, so the optional
 * `instalment_loading` rung (FR-252) appears exactly when the algorithm mounts it. Each bar
 * floats from the previous rung's value to this one's; the table beside it carries the
 * rung's value, its change, and the operation that produced it (FR-248).
 *
 * **Per-peril components are not shown** (FR-249, R6.1, `RL-1459`, `OQ-1460`): a rung's
 * optional `components` field has no producer yet, so nothing here reads it. The view limb
 * is carried with the question, and a test asserts the absence.
 */
import { BarChart } from "echarts/charts";
import { GridComponent, LegendComponent, TooltipComponent } from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { computed } from "vue";
import VChart from "vue-echarts";

import { formatMinor } from "@/api/versions";
import type { LadderRung } from "@/api/score";
import type { Column } from "@/chart-table";
import ChartFigure from "@/components/ChartFigure.vue";

import { describeOperation, rungChanges } from "./ladder";

use([BarChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

const props = defineProps<{
  rungs: readonly LadderRung[];
  /** ISO 4217. The API carries no workspace currency yet (OQ-551), so the view names one. */
  currency: string;
}>();

const rows = computed(() => rungChanges(props.rungs));

const columns = computed<readonly Column<(typeof rows.value)[number]>[]>(() => [
  { key: "rung", label: "Rung", value: (row) => row.rung.rung },
  { key: "value", label: "Value", value: (row) => formatMinor(row.rung.value_minor, props.currency) },
  {
    key: "change",
    label: "Change",
    value: (row) => (row.change === null ? "" : formatMinor(row.change, props.currency)),
  },
  { key: "operation", label: "Operation", value: (row) => describeOperation(row.rung.operation) },
]);

/** Floating bars: an invisible base, then the rise, the fall, or a whole-bar total. */
const option = computed(() => ({
  tooltip: { trigger: "axis" as const, axisPointer: { type: "shadow" as const } },
  legend: { data: ["Total", "Increase", "Decrease"], bottom: 0 },
  grid: { left: 70, right: 30, top: 20, bottom: 60 },
  xAxis: { type: "category" as const, data: rows.value.map((row) => row.rung.rung) },
  yAxis: { type: "value" as const, name: "Minor units" },
  series: [
    {
      name: "Base",
      type: "bar" as const,
      stack: "ladder",
      itemStyle: { color: "transparent" },
      data: rows.value.map((row) => row.base),
    },
    {
      name: "Total",
      type: "bar" as const,
      stack: "ladder",
      data: rows.value.map((row) => (row.kind === "total" ? row.size : null)),
    },
    {
      name: "Increase",
      type: "bar" as const,
      stack: "ladder",
      data: rows.value.map((row) => (row.kind === "increase" ? row.size : null)),
    },
    {
      name: "Decrease",
      type: "bar" as const,
      stack: "ladder",
      data: rows.value.map((row) => (row.kind === "decrease" ? row.size : null)),
    },
  ],
}));
</script>

<template>
  <ChartFigure
    title="Premium ladder"
    caption="Each rung's value, and the change from the rung before it."
    :columns="columns"
    :rows="rows"
  >
    <VChart
      class="h-80 w-full"
      :option="option"
      autoresize
    />
  </ChartFigure>
</template>
