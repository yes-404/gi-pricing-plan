<script setup lang="ts">
import { LineChart } from "echarts/charts";
import { GridComponent, LegendComponent, TooltipComponent } from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { computed } from "vue";
import VChart from "vue-echarts";

import type { PartitionCaption, PartitionDiagnostics } from "@/api/diagnostics";
import ChartFigure from "@/components/ChartFigure.vue";

use([LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

const props = defineProps<{
  partitions: readonly (readonly [PartitionCaption, PartitionDiagnostics])[];
}>();

/**
 * Predicted against actual by predicted decile (FR-MODEL-50), both partitions on one axis.
 *
 * Four series and not two: the instrument is the *gap* between predicted and actual within a
 * partition, and a chart plotting only one of them per partition shows a ranking rather than
 * a calibration. The train pair and the holdout pair are then read against each other, which
 * is what FR-MODEL-54 asks for.
 */
const bins = computed(() => {
  const seen: number[] = [];
  for (const [, partition] of props.partitions) {
    for (const bin of partition.lift) if (!seen.includes(bin.bin)) seen.push(bin.bin);
  }
  return seen.sort((a, b) => a - b);
});

const LINE_TYPES = ["solid", "dashed", "dotted", "dashdot"] as const;

const series = computed(() =>
  props.partitions.flatMap(([label, partition], partitionIndex) =>
    (["predicted", "actual"] as const).map((measure, measureIndex) => ({
      name: `${label} ${measure}`,
      type: "line" as const,
      data: bins.value.map(
        (bin) => partition.lift.find((candidate) => candidate.bin === bin)?.[measure] ?? null,
      ),
      // NFR-OVR-10: four series need four distinguishable line types, not four hues.
      lineStyle: { type: LINE_TYPES[partitionIndex * 2 + measureIndex] ?? "solid", width: 2 },
    })),
  ),
);

const option = computed(() => ({
  tooltip: { trigger: "axis" as const },
  legend: { data: series.value.map((s) => s.name), bottom: 0 },
  grid: { left: 60, right: 30, top: 20, bottom: 60 },
  xAxis: { type: "category" as const, data: bins.value.map(String) },
  yAxis: { type: "value" as const, name: "Response" },
  series: series.value,
}));

const columns = computed(() => [
  "Bin",
  ...props.partitions.flatMap(([label]) => [
    `${label} rows`,
    `${label} predicted`,
    `${label} actual`,
  ]),
]);

const rows = computed(() =>
  bins.value.map((bin) => [
    bin,
    ...props.partitions.flatMap(([, partition]) => {
      const found = partition.lift.find((candidate) => candidate.bin === bin);
      return [found?.rows ?? null, found?.predicted ?? null, found?.actual ?? null];
    }),
  ]),
);
</script>

<template>
  <ChartFigure
    title="Lift by decile"
    caption="Predicted and actual response in each predicted decile, train and holdout."
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
