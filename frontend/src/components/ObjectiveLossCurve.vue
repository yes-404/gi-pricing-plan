<script setup lang="ts">
import { LineChart } from "echarts/charts";
import { GridComponent, TooltipComponent } from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { computed } from "vue";
import VChart from "vue-echarts";

import type { ObjectivePreviewCurve } from "@/api/objectives";
import type { Column } from "@/chart-table";
import ChartFigure from "@/components/ChartFigure.vue";

use([LineChart, GridComponent, TooltipComponent, CanvasRenderer]);

const props = defineProps<{ curve: ObjectivePreviewCurve }>();

/**
 * The loss at each score the preview route returned (`02` §5.3, FR-8140), drawn as given:
 * the route evaluated it with the fit's own kernel, so nothing here computes a value. A point
 * the route reports as `null` (non-finite) stays a gap in the line and a dash in the table.
 */
const scores = computed(() => props.curve.f.map((value) => Number(value.toPrecision(6))));

const option = computed(() => ({
  tooltip: { trigger: "axis" as const },
  grid: { left: 60, right: 30, top: 20, bottom: 40 },
  xAxis: { type: "category" as const, name: "Score f", data: scores.value.map(String) },
  yAxis: { type: "value" as const, name: "Loss" },
  series: [{ name: "Loss", type: "line" as const, symbol: "circle", data: props.curve.loss }],
}));

const rows = computed(() => props.curve.f.map((_, index) => index));

const columns = computed<readonly Column<number>[]>(() => [
  { key: "f", label: "Score f", value: (index) => scores.value[index] ?? null },
  { key: "loss", label: "Loss", value: (index) => props.curve.loss[index] ?? null },
]);
</script>

<template>
  <ChartFigure
    title="Loss curve"
    caption="The per-observation loss against the raw score f, at the chosen parameter values."
    :columns="columns"
    :rows="rows"
  >
    <VChart
      class="h-72 w-full"
      :option="option"
      autoresize
    />
  </ChartFigure>
</template>
