<script setup lang="ts">
import { LineChart } from "echarts/charts";
import { GridComponent, LegendComponent, TooltipComponent } from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { computed } from "vue";
import VChart from "vue-echarts";

import type { GbmEvalPoint } from "@/api/diagnostics";
import ChartFigure from "@/components/ChartFigure.vue";

use([LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

const props = defineProps<{ evalCurve: readonly GbmEvalPoint[] }>();

/**
 * The evaluation metric per boosting iteration, train against holdout (FR-MODEL-52).
 *
 * This is the second of the two partitioned surfaces in the whole contract — `GbmEvalPoint`
 * declares `train` and `holdout` per iteration while the importances beside it declare
 * neither (FR-MODEL-54, as scoped 2026-08-24). It is the overfitting chart: the iteration
 * where holdout turns while train keeps falling is the answer a reader comes here for, and it
 * exists only because both series share one axis.
 *
 * Both fields are nullable, and a gap stays `null` rather than being interpolated — ECharts
 * breaks the line at a null, which is the honest rendering of an iteration that recorded no
 * value for that partition. The contract's own validator refuses a point reporting neither,
 * so a row can be half empty but never entirely so.
 *
 * The axis is labelled with the **recorded** `iteration` rather than the array position:
 * nothing in the contract says the curve is dense or zero-based, and a long boosting run
 * recorded at an interval would otherwise report the wrong stopping point.
 */
const iterations = computed(() => props.evalCurve.map((point) => String(point.iteration)));

const metric = computed(() => props.evalCurve[0]?.metric ?? "metric");

const series = computed(() => [
  {
    name: "Train",
    type: "line" as const,
    symbol: "none",
    data: props.evalCurve.map((point) => point.train ?? null),
    // NFR-OVR-10: line type carries the partition where hue alone cannot.
    lineStyle: { type: "solid" as const, width: 2 },
  },
  {
    name: "Holdout",
    type: "line" as const,
    symbol: "none",
    data: props.evalCurve.map((point) => point.holdout ?? null),
    lineStyle: { type: "dashed" as const, width: 2 },
  },
]);

const option = computed(() => ({
  tooltip: { trigger: "axis" as const },
  legend: { data: ["Train", "Holdout"], bottom: 0 },
  grid: { left: 70, right: 30, top: 20, bottom: 50 },
  xAxis: { type: "category" as const, name: "Iteration", data: iterations.value },
  yAxis: { type: "value" as const, name: metric.value, scale: true },
  series: series.value,
}));

const columns = ["Iteration", "Train", "Holdout"] as const;

const rows = computed(() =>
  props.evalCurve.map((point) => [point.iteration, point.train ?? null, point.holdout ?? null]),
);
</script>

<template>
  <ChartFigure
    title="Evaluation curve"
    :caption="`${metric} per boosting iteration. Where holdout turns and train keeps falling is where the model began fitting noise.`"
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
