<script setup lang="ts">
import { LineChart } from "echarts/charts";
import { GridComponent, LegendComponent, TooltipComponent } from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { computed } from "vue";
import VChart from "vue-echarts";

import type { PartitionCaption, PartitionDiagnostics } from "@/api/diagnostics";
import type { Column } from "@/chart-table";
import ChartFigure from "@/components/ChartFigure.vue";

use([LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

const props = defineProps<{
  partitions: readonly (readonly [PartitionCaption, PartitionDiagnostics])[];
}>();

/**
 * Actual over expected by factor level (FR-171), train and holdout on one axis.
 *
 * Two charts side by side would carry two y-axes and invite the reader to compare positions
 * rather than values; FR-183 asks for the comparison, so both partitions share an axis.
 *
 * The key is factor **and** level: `level` alone is not unique across factors — "0-3" can
 * belong to vehicle age and to years-since-claim on the same model — and an axis keyed on it
 * silently merges two rows into one.
 */
const key = (cell: { factor: string; level: string }) => `${cell.factor} · ${cell.level}`;

const levels = computed(() => {
  const seen: string[] = [];
  for (const [, partition] of props.partitions) {
    for (const cell of partition.ae_by_factor) {
      const label = key(cell);
      if (!seen.includes(label)) seen.push(label);
    }
  }
  return seen;
});

const LINE_TYPES = ["solid", "dashed", "dotted"] as const;

const series = computed(() =>
  props.partitions.map(([label, partition], index) => ({
    name: label,
    type: "line" as const,
    data: levels.value.map(
      (level) => partition.ae_by_factor.find((cell) => key(cell) === level)?.ae ?? null,
    ),
    // NFR-463: hue alone is not a channel. The line type carries the same distinction.
    lineStyle: { type: LINE_TYPES[index] ?? "solid", width: 2 },
  })),
);

const option = computed(() => ({
  tooltip: { trigger: "axis" as const },
  legend: { data: props.partitions.map(([label]) => label), bottom: 0 },
  grid: { left: 60, right: 30, top: 20, bottom: 60 },
  xAxis: { type: "category" as const, data: levels.value, axisLabel: { rotate: 45 } },
  yAxis: { type: "value" as const, name: "A/E" },
  series: series.value,
}));

/**
 * `exposure_years` is an exact decimal **string** (FR-10) and is passed through as one.
 * It is not plotted and nothing computes with it, so there is no reason to widen it to a
 * float here — the string is what the fit recorded.
 *
 * The rows are the level labels, and each partition's column looks its cell up by that label.
 * Keys use the partition's index, never its caption: a caption is display text, and two
 * partitions captioned alike must not produce a duplicate key.
 */
const columns = computed<readonly Column<string>[]>(() => [
  { key: "level", label: "Factor and level", value: (level) => level },
  ...props.partitions.flatMap(([label, partition], index): Column<string>[] => {
    const cellAt = (level: string) =>
      partition.ae_by_factor.find((candidate) => key(candidate) === level);
    return [
      { key: `p${index}-ae`, label: `${label} A/E`, value: (level) => cellAt(level)?.ae ?? null },
      {
        key: `p${index}-exposure-years`,
        label: `${label} exposure years`,
        value: (level) => cellAt(level)?.exposure_years ?? null,
      },
    ];
  }),
]);
</script>

<template>
  <ChartFigure
    title="A/E by factor"
    caption="Actual over expected at each factor level, exposure shown beside it."
    :columns="columns"
    :rows="levels"
  >
    <VChart
      class="h-80 w-full"
      :option="option"
      autoresize
    />
  </ChartFigure>
</template>
