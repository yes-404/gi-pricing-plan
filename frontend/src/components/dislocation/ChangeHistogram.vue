<script setup lang="ts">
/**
 * The change distribution as a histogram with its table (03 FR-263, NFR-463): one bar per
 * band of the run's `distribution`, in the order the run gives them (the half-open bands of
 * §4.6, an empty band listed with 0 policies).
 */
import { BarChart } from "echarts/charts";
import { GridComponent, TooltipComponent } from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { computed } from "vue";
import VChart from "vue-echarts";

import type { DislocationBand } from "@/api/dislocationRuns";
import type { Column } from "@/chart-table";
import ChartFigure from "@/components/ChartFigure.vue";

import { formatPct, formatShare } from "./format";

use([BarChart, GridComponent, TooltipComponent, CanvasRenderer]);

const props = defineProps<{ bands: readonly DislocationBand[] }>();

const columns: readonly Column<DislocationBand>[] = [
  { key: "band", label: "Band", value: (row) => row.band },
  { key: "policies", label: "Policies", value: (row) => row.policies },
  { key: "exposure", label: "Exposure share", value: (row) => formatShare(row.exposure_share) },
  { key: "mean", label: "Mean change", value: (row) => formatPct(row.mean_change_pct) },
];

const option = computed(() => ({
  tooltip: { trigger: "axis" as const },
  grid: { left: 60, right: 20, top: 20, bottom: 50 },
  xAxis: { type: "category" as const, data: props.bands.map((b) => b.band) },
  yAxis: { type: "value" as const, name: "Policies" },
  series: [{ name: "Policies", type: "bar" as const, data: props.bands.map((b) => b.policies) }],
}));
</script>

<template>
  <ChartFigure
    title="Change distribution"
    caption="Policies in each band of premium change, candidate against baseline."
    :columns="columns"
    :rows="bands"
  >
    <VChart
      class="h-72 w-full"
      :option="option"
      autoresize
    />
  </ChartFigure>
</template>
