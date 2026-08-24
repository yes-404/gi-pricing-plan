<script setup lang="ts">
import { BarChart, LineChart } from "echarts/charts";
import { GridComponent, LegendComponent, TooltipComponent } from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { computed } from "vue";
import VChart from "vue-echarts";

import type { DoubleLift } from "@/api/comparisons";

use([BarChart, LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

const props = defineProps<{ series: DoubleLift }>();

/**
 * Bins in the artifact's own order. `02` §4.11 orders them by the **ratio** of the two
 * predictions, which is what makes the chart answer "where the models disagree, which one is
 * right?"; re-sorting by either prediction answers the weaker question instead.
 */
const bins = computed(() => props.series.bins);

const labels = computed(() => bins.value.map((b) => String(b.bin)));

/**
 * `exposure_years` is a `DecimalStr` — exact decimal, carried as a string, so a float never
 * silently rounds it (FR-OVR-7's rule about the rating path; here it is a diagnostic read and
 * the conversion is safe). It is also nullable, and a bar chart with holes in it reads as
 * zero exposure rather than as unknown exposure, so the whole series is omitted unless every
 * bin has one.
 */
const exposure = computed(() => {
  const raw = bins.value.map((b) => b.exposure_years);
  return raw.every((v) => typeof v === "string") ? raw.map((v) => Number(v)) : null;
});

const option = computed(() => ({
  tooltip: { trigger: "axis" as const },
  legend: { bottom: 0 },
  grid: { left: 56, right: 56, top: 16, bottom: 56 },
  xAxis: {
    type: "category" as const,
    data: labels.value,
    name: "Bin (by prediction ratio)",
    nameLocation: "middle" as const,
    nameGap: 30,
  },
  yAxis: [
    { type: "value" as const, name: "Rate", position: "left" as const },
    ...(exposure.value
      ? [
          {
            type: "value" as const,
            name: "Exposure",
            position: "right" as const,
            splitLine: { show: false },
          },
        ]
      : []),
  ],
  series: [
    // Grey is reserved for exposure across every chart in this app (HistogramChart.vue).
    ...(exposure.value
      ? [
          {
            name: "Exposure",
            type: "bar" as const,
            yAxisIndex: 1,
            data: exposure.value,
            itemStyle: { color: "#cbd5e1" },
          },
        ]
      : []),
    // Actual is the reference truth, so it takes the neutral darkest and a solid line. The
    // three lines differ by line type as well as by hue, which is what NFR-OVR-10's WCAG
    // obligation needs.
    {
      name: "Actual",
      type: "line" as const,
      data: bins.value.map((b) => b.actual),
      itemStyle: { color: "#0f172a" },
      lineStyle: { color: "#0f172a", type: "solid" as const, width: 2 },
    },
    {
      name: "Baseline predicted",
      type: "line" as const,
      data: bins.value.map((b) => b.baseline_predicted),
      itemStyle: { color: "#0f766e" },
      lineStyle: { color: "#0f766e", type: "dashed" as const, width: 2 },
    },
    {
      name: "Challenger predicted",
      type: "line" as const,
      data: bins.value.map((b) => b.challenger_predicted),
      itemStyle: { color: "#b45309" },
      lineStyle: { color: "#b45309", type: "dotted" as const, width: 2 },
    },
  ],
}));
</script>

<template>
  <div>
    <VChart
      class="h-80 w-full"
      :option="option"
      autoresize
    />
  </div>
</template>
