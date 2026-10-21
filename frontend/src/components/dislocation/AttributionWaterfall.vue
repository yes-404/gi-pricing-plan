<script setup lang="ts">
/**
 * The attribution waterfall with its table (03 FR-266, NFR-463): one step per change group, each
 * bar floating from the cumulative total before it. The step's value is the group's exact
 * Shapley amount, or its isolated amount where the run is `order_dependent` (§4.6). The
 * residual and the method are stated beside it, never dropped.
 */
import { BarChart } from "echarts/charts";
import { GridComponent, LegendComponent, TooltipComponent } from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { computed } from "vue";
import VChart from "vue-echarts";

import type { AttributionItem, AttributionSummary } from "@/api/dislocationRuns";
import type { Column } from "@/chart-table";
import ChartFigure from "@/components/ChartFigure.vue";

import { formatMinor, formatPct } from "./format";

use([BarChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

const props = defineProps<{
  items: readonly AttributionItem[] | null | undefined;
  summary: AttributionSummary | null | undefined;
}>();

interface Step {
  readonly group: string;
  readonly value: number;
  readonly base: number;
  readonly cumulative: number;
  readonly meanPct: number | null;
}

/** `shapley_minor`, or `isolated_minor` under `order_dependent` where it is null. */
const steps = computed<Step[]>(() =>
  (props.items ?? []).map((item) => {
    const value = item.shapley_minor ?? item.isolated_minor;
    return {
      group: item.group,
      value,
      base: Math.min(item.cumulative_minor - value, item.cumulative_minor),
      cumulative: item.cumulative_minor,
      meanPct: item.mean_change_pct,
    };
  }),
);

const valueLabel = computed(() =>
  props.summary?.method === "order_dependent" ? "Isolated change" : "Shapley change",
);

const columns = computed<readonly Column<Step>[]>(() => [
  { key: "group", label: "Change group", value: (row) => row.group },
  { key: "value", label: valueLabel.value, value: (row) => formatMinor(row.value) },
  { key: "cumulative", label: "Cumulative", value: (row) => formatMinor(row.cumulative) },
  { key: "mean", label: "Mean change", value: (row) => formatPct(row.meanPct) },
]);

const option = computed(() => ({
  tooltip: { trigger: "axis" as const, axisPointer: { type: "shadow" as const } },
  legend: { data: ["Increase", "Decrease"], bottom: 0 },
  grid: { left: 70, right: 30, top: 20, bottom: 60 },
  xAxis: { type: "category" as const, data: steps.value.map((s) => s.group) },
  yAxis: { type: "value" as const, name: "Minor units (currency not configured, OQ-551)" },
  series: [
    {
      name: "Base",
      type: "bar" as const,
      stack: "attribution",
      itemStyle: { color: "transparent" },
      data: steps.value.map((s) => s.base),
    },
    {
      name: "Increase",
      type: "bar" as const,
      stack: "attribution",
      data: steps.value.map((s) => (s.value >= 0 ? s.value : null)),
    },
    {
      name: "Decrease",
      type: "bar" as const,
      stack: "attribution",
      data: steps.value.map((s) => (s.value < 0 ? -s.value : null)),
    },
  ],
}));
</script>

<template>
  <div v-if="steps.length > 0">
    <ChartFigure
      title="Attribution"
      caption="The total change split across the declared change groups. Amounts are in major units; currency not configured (OQ-551)."
      :columns="columns"
      :rows="steps"
    >
      <VChart
        class="h-72 w-full"
        :option="option"
        autoresize
      />
    </ChartFigure>
    <dl
      v-if="summary"
      class="mt-3 grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-sm"
    >
      <dt class="text-slate-500">
        Method
      </dt>
      <dd>{{ summary.method }} ({{ summary.subset_valuation }})</dd>
      <dt class="text-slate-500">
        Total change
      </dt>
      <dd>{{ formatMinor(summary.total_change_minor) }}</dd>
      <dt class="text-slate-500">
        Residual
      </dt>
      <dd>{{ formatMinor(summary.residual_minor) }}</dd>
      <template v-if="summary.method === 'order_dependent'">
        <dt class="text-slate-500">
          Order sensitivity lower bound
        </dt>
        <dd>{{ summary.order_sensitivity_lower_bound ?? "—" }}</dd>
        <dt class="text-slate-500">
          Orders sampled
        </dt>
        <dd>{{ summary.orders_sampled ?? "—" }}</dd>
      </template>
    </dl>
    <p
      v-if="summary?.replay_fell_back"
      role="status"
      class="mt-2 text-sm text-slate-600"
    >
      Ladder replay did not match the re-rate, so this run's subsets were valued by re-rating.
    </p>
  </div>
  <p
    v-else
    class="mt-6 text-sm text-slate-500"
  >
    This run carries no attribution.
  </p>
</template>
