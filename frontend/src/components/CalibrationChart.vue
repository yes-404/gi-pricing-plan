<script setup lang="ts">
import { LineChart, ScatterChart } from "echarts/charts";
import { GridComponent, LegendComponent, TooltipComponent } from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { computed } from "vue";
import VChart from "vue-echarts";

import type { PartitionCaption, PartitionDiagnostics } from "@/api/diagnostics";
import ChartFigure from "@/components/ChartFigure.vue";

use([ScatterChart, LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

const props = defineProps<{
  partitions: readonly (readonly [PartitionCaption, PartitionDiagnostics])[];
}>();

/**
 * Calibration by predicted decile (FR-171): predicted on x, actual on y, so a
 * well-calibrated model lies on the diagonal.
 *
 * Plotted against the bin index instead, the same numbers make a rising line for every model
 * and say nothing — the diagonal is the whole instrument, which is why it is drawn as a
 * series rather than left to the reader.
 */
const SYMBOLS = ["circle", "triangle", "diamond"] as const;

const points = computed(() =>
  props.partitions.map(([label, partition], index) => ({
    name: label,
    type: "scatter" as const,
    // NFR-463: symbol shape carries the partition where hue cannot.
    symbol: SYMBOLS[index] ?? "circle",
    symbolSize: 10,
    data: partition.calibration.map((bin) => [bin.predicted, bin.actual]),
  })),
);

const extent = computed(() => {
  const values = props.partitions.flatMap(([, partition]) =>
    partition.calibration.flatMap((bin) => [bin.predicted, bin.actual]),
  );
  return values.length === 0 ? [0, 1] : [Math.min(...values), Math.max(...values)];
});

const option = computed(() => ({
  tooltip: { trigger: "item" as const },
  legend: { data: [...props.partitions.map(([label]) => label), "Perfect calibration"], bottom: 0 },
  grid: { left: 60, right: 30, top: 20, bottom: 60 },
  xAxis: { type: "value" as const, name: "Predicted" },
  yAxis: { type: "value" as const, name: "Actual" },
  series: [
    ...points.value,
    {
      name: "Perfect calibration",
      type: "line" as const,
      symbol: "none",
      data: [
        [extent.value[0], extent.value[0]],
        [extent.value[1], extent.value[1]],
      ],
      lineStyle: { type: "dotted" as const, width: 1 },
    },
  ],
}));

const bins = computed(() => {
  const seen: number[] = [];
  for (const [, partition] of props.partitions) {
    for (const bin of partition.calibration) if (!seen.includes(bin.bin)) seen.push(bin.bin);
  }
  return seen.sort((a, b) => a - b);
});

const columns = computed(() => [
  "Bin",
  ...props.partitions.flatMap(([label]) => [`${label} predicted`, `${label} actual`]),
]);

const rows = computed(() =>
  bins.value.map((bin) => [
    bin,
    ...props.partitions.flatMap(([, partition]) => {
      const found = partition.calibration.find((candidate) => candidate.bin === bin);
      return [found?.predicted ?? null, found?.actual ?? null];
    }),
  ]),
);
</script>

<template>
  <ChartFigure
    title="Calibration by decile"
    caption="Predicted against actual in each decile. Points on the dotted diagonal are calibrated."
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
