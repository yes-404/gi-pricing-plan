<script setup lang="ts">
/**
 * The segment breakdown (03 FR-264): the run sliced by each declared Factor, and by the
 * ladder rung at which the change originated. Both are tables — a grid is the figure — and
 * the rung contributions also draw as bars with their table (NFR-463).
 */
import { BarChart } from "echarts/charts";
import { GridComponent, TooltipComponent } from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { computed } from "vue";
import VChart from "vue-echarts";

import type { RungContribution, SegmentSlice } from "@/api/dislocationRuns";
import type { Column } from "@/chart-table";
import ChartFigure from "@/components/ChartFigure.vue";

import { formatPct, formatShare } from "./format";

use([BarChart, GridComponent, TooltipComponent, CanvasRenderer]);

const props = defineProps<{
  segments: readonly SegmentSlice[];
  rungs: readonly RungContribution[];
}>();

const segmentColumns: readonly Column<SegmentSlice>[] = [
  { key: "factor", label: "Factor", value: (row) => row.factor },
  { key: "level", label: "Level", value: (row) => row.level ?? "(missing)" },
  { key: "policies", label: "Policies", value: (row) => row.policies },
  { key: "exposure", label: "Exposure share", value: (row) => formatShare(row.exposure_share) },
  { key: "mean", label: "Mean change", value: (row) => formatPct(row.mean_change_pct) },
];

const rungColumns: readonly Column<RungContribution>[] = [
  { key: "rung", label: "Ladder rung", value: (row) => row.rung },
  { key: "contribution", label: "Contribution", value: (row) => formatPct(row.contribution_pct) },
];

const rungOption = computed(() => ({
  tooltip: { trigger: "axis" as const },
  grid: { left: 60, right: 20, top: 20, bottom: 50 },
  xAxis: { type: "category" as const, data: props.rungs.map((r) => r.rung) },
  yAxis: { type: "value" as const, name: "Contribution (%)" },
  series: [
    {
      name: "Contribution",
      type: "bar" as const,
      data: props.rungs.map((r) => r.contribution_pct),
    },
  ],
}));
</script>

<template>
  <div>
    <ChartFigure
      v-if="segments.length > 0"
      title="Change by segment"
      caption="Mean premium change for each level of each declared segment Factor."
      :columns="segmentColumns"
      :rows="segments"
    />
    <p
      v-else
      class="mt-6 text-sm text-slate-500"
    >
      The run declared no segments.
    </p>

    <ChartFigure
      v-if="rungs.length > 0"
      title="Change by ladder rung"
      caption="The share of the change that originates at each Premium Ladder rung."
      :columns="rungColumns"
      :rows="rungs"
    >
      <VChart
        class="h-64 w-full"
        :option="rungOption"
        autoresize
      />
    </ChartFigure>
  </div>
</template>
