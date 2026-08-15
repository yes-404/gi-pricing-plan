<script setup lang="ts">
import { BarChart, CustomChart, LineChart } from "echarts/charts";
import {
  DataZoomComponent,
  GridComponent,
  LegendComponent,
  TooltipComponent,
} from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { computed } from "vue";
import VChart from "vue-echarts";

import type { OneWaySummary } from "@/api/profiles";

use([BarChart, LineChart, CustomChart, GridComponent, TooltipComponent, LegendComponent,
     DataZoomComponent, CanvasRenderer]);

const props = defineProps<{ summary: OneWaySummary }>();

const rows = computed(() => props.summary.rows ?? []);
const levels = computed(() => rows.value.map((row) => row.level));

/**
 * Exposure as bars, frequency as a line, on two axes.
 *
 * The pairing is the point of a one-way: a level with a high frequency and almost no
 * exposure is noise, and the chart has to make that visible at a glance rather than invite
 * an actuary to rate on four policies.
 *
 * `exposure_years` is an exact decimal **string** (FR-OVR-7). `Number()` here is
 * deliberate and safe: a chart coordinate is a float64 either way, and the value being
 * plotted is not the value being stored. Nothing computes with it.
 */
const option = computed(() => ({
  tooltip: { trigger: "axis" as const },
  legend: { data: ["Exposure", "Frequency"], bottom: 0 },
  grid: { left: 60, right: 60, top: 20, bottom: 50 },
  xAxis: { type: "category" as const, data: levels.value, axisLabel: { rotate: 45 } },
  yAxis: [
    { type: "value" as const, name: "Exposure", position: "left" as const },
    { type: "value" as const, name: "Frequency", position: "right" as const },
  ],
  series: [
    {
      name: "Exposure",
      type: "bar" as const,
      data: rows.value.map((row) => Number(row.exposure_years)),
      itemStyle: { color: "#cbd5e1" },
      yAxisIndex: 0,
    },
    {
      name: "Frequency",
      type: "line" as const,
      data: rows.value.map((row) => row.frequency),
      yAxisIndex: 1,
      symbolSize: 6,
      lineStyle: { color: "#0f766e" },
      itemStyle: { color: "#0f766e" },
    },
    {
      // The exact Poisson interval (FR-DATA-26), drawn as a whisker per level. A
      // frequency without one invites a decision the count cannot support — nine claims
      // in a young-driver band look either significant or like noise depending entirely
      // on this.
      name: "Frequency CI",
      type: "custom" as const,
      yAxisIndex: 1,
      silent: true,
      renderItem: renderInterval,
      encode: { x: 0, y: [1, 2] },
      data: rows.value.map((row, index) => [
        index,
        row.frequency_ci?.[0] ?? null,
        row.frequency_ci?.[1] ?? null,
      ]),
    },
  ],
}));

function renderInterval(params: unknown, api: unknown): unknown {
  const a = api as {
    value: (index: number) => number;
    coord: (point: [number, number]) => [number, number];
    size: (value: [number, number]) => [number, number];
  };
  const low = a.value(1);
  const high = a.value(2);
  if (low == null || high == null || Number.isNaN(low)) return undefined;

  const [x, yLow] = a.coord([a.value(0), low]);
  const [, yHigh] = a.coord([a.value(0), high]);
  const halfWidth = Math.max(a.size([1, 0])[0] * 0.15, 2);
  const style = { stroke: "#0f766e", lineWidth: 1, opacity: 0.7 };

  return {
    type: "group",
    children: [
      { type: "line", shape: { x1: x, y1: yLow, x2: x, y2: yHigh }, style },
      { type: "line", shape: { x1: x - halfWidth, y1: yLow, x2: x + halfWidth, y2: yLow }, style },
      { type: "line", shape: { x1: x - halfWidth, y1: yHigh, x2: x + halfWidth, y2: yHigh }, style },
    ],
  };
}
</script>

<template>
  <div>
    <VChart
      v-if="rows.length"
      class="h-80 w-full"
      :option="option"
      autoresize
    />
    <p
      v-else
      class="text-sm text-slate-500"
    >
      This column has no stored one-way.
    </p>
  </div>
</template>
