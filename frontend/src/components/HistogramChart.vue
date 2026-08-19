<script setup lang="ts">
import { BarChart } from "echarts/charts";
import { GridComponent, LegendComponent, TooltipComponent } from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { computed } from "vue";
import VChart from "vue-echarts";

import type { Histogram } from "@/api/profiles";

use([BarChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

const props = defineProps<{ histogram: Histogram }>();

const edges = computed(() => props.histogram.edges ?? []);
const counts = computed(() => props.histogram.counts ?? []);
const exposure = computed(() => props.histogram.exposure ?? []);

function format(edge: number | undefined): string {
  if (edge == null) return "";
  return Number.isInteger(edge) ? String(edge) : edge.toFixed(2);
}

/** Bin labels from the edges: FR-DATA-48 stores one more edge than it stores counts. */
const labels = computed(() =>
  counts.value.map((_, i) => `${format(edges.value[i])}–${format(edges.value[i + 1])}`),
);

/**
 * Rows as bars, and exposure beside them when the profile weighted the bins.
 *
 * Exposure is an exact decimal **string** (FR-OVR-7). `Number()` here is deliberate and
 * safe, for the reason `OneWayChart` gives: a chart coordinate is a float64 either way and
 * nothing computes with the plotted value.
 */
const option = computed(() => ({
  tooltip: { trigger: "axis" as const },
  legend: { data: exposure.value.length ? ["Rows", "Exposure"] : ["Rows"], bottom: 0 },
  grid: { left: 50, right: 50, top: 16, bottom: 46 },
  xAxis: { type: "category" as const, data: labels.value, axisLabel: { rotate: 45 } },
  yAxis: [
    { type: "value" as const, name: "Rows", position: "left" as const },
    ...(exposure.value.length
      ? [{ type: "value" as const, name: "Exposure", position: "right" as const }]
      : []),
  ],
  series: [
    {
      name: "Rows",
      type: "bar" as const,
      data: counts.value,
      itemStyle: { color: "#cbd5e1" },
      yAxisIndex: 0,
    },
    ...(exposure.value.length
      ? [
          {
            name: "Exposure",
            type: "bar" as const,
            yAxisIndex: 1,
            data: exposure.value.map((e) => Number(e)),
            itemStyle: { color: "#0f766e" },
          },
        ]
      : []),
  ],
}));
</script>

<template>
  <VChart
    class="h-40 w-full"
    :option="option"
    autoresize
  />
</template>
