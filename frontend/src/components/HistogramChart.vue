<script setup lang="ts">
import { BarChart } from "echarts/charts";
import { GridComponent, LegendComponent, TooltipComponent } from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { computed } from "vue";
import VChart from "vue-echarts";

import type { Histogram } from "@/api/profiles";
import ChartFigure from "@/components/ChartFigure.vue";

use([BarChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

const props = defineProps<{
  histogram: Histogram;
  /**
   * The column this histogram describes. Required, not optional with a fallback: the
   * Profile page renders one of these per column, and `ChartFigure` names its table after
   * its title, so a shared or absent name would leave a screen-reader user with a page of
   * identically-named tables and no way to tell which column each belongs to.
   */
  column: string;
}>();

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
 *
 * Colours match `OneWayChart`'s, and the rule is that **exposure is always the pale grey
 * `#cbd5e1`**. Both charts appear on the Profile page against the same column, so exposure
 * changing colour between them would read as two different quantities.
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
      itemStyle: { color: "#0f766e" },
      yAxisIndex: 0,
    },
    ...(exposure.value.length
      ? [
          {
            name: "Exposure",
            type: "bar" as const,
            yAxisIndex: 1,
            data: exposure.value.map((e) => Number(e)),
            itemStyle: { color: "#cbd5e1" },
          },
        ]
      : []),
  ],
}));

/**
 * The chart's accessible equivalent (NFR-OVR-10).
 *
 * The Exposure column is dropped rather than dashed when the profile weighted nothing,
 * matching the chart, which drops the series and the second axis in the same case. A column
 * of em dashes would say the histogram has an exposure of nothing, which is a different
 * claim from its having no exposure at all. This is the reactive case `ChartFigure`'s arity
 * guard exists to cover: `columns` and `rows` both narrow, and they must narrow together.
 */
const columns = computed(() =>
  exposure.value.length ? ["Bin", "Rows", "Exposure"] : ["Bin", "Rows"],
);

/**
 * Exposure is passed through as the exact decimal **string** it is stored as (FR-OVR-7).
 * The chart widens it to a float because a coordinate is one either way; the table has no
 * such excuse, and `AeByFactorChart` set this precedent for the same reason.
 */
const rows = computed(() =>
  labels.value.map((label, i) => [
    label,
    counts.value[i] ?? null,
    ...(exposure.value.length ? [exposure.value[i] ?? null] : []),
  ]),
);
</script>

<template>
  <ChartFigure
    :title="`Distribution of ${column}`"
    :caption="
      exposure.length
        ? 'Rows falling in each bin, with the exposure years the profile weighted them by.'
        : 'Rows falling in each bin.'
    "
    :columns="columns"
    :rows="rows"
  >
    <VChart
      class="h-40 w-full"
      :option="option"
      autoresize
    />
  </ChartFigure>
</template>
