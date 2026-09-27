<script setup lang="ts">
import { LineChart, ScatterChart } from "echarts/charts";
import { GridComponent, LegendComponent, TooltipComponent } from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { computed } from "vue";
import VChart from "vue-echarts";

import type { CrossValidationDiagnostics } from "@/api/diagnostics";
import ChartFigure from "@/components/ChartFigure.vue";

use([LineChart, ScatterChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

const props = defineProps<{ crossValidation: CrossValidationDiagnostics }>();

/**
 * Cross-validation with declared fold construction and a persisted seed (FR-182).
 *
 * Unpartitioned: `CrossValidationDiagnostics` declares neither `train` nor `holdout`, because
 * the fold path is a property of one fitting procedure rather than a measurement against a
 * held-out population — each fold is its own holdout, which is the point of the method.
 *
 * The path plots the mean with a ±1 std band rather than the mean alone: FR-182 requires
 * dispersion to be persisted, and an alpha chosen off a mean whose neighbours are within one
 * standard error was not really chosen.
 */
const alphas = computed(() => props.crossValidation.path.map((point) => String(point.alpha)));

const pathOption = computed(() => ({
  tooltip: { trigger: "axis" as const },
  legend: { data: ["Mean score", "Mean + 1 std", "Mean − 1 std"], bottom: 0 },
  grid: { left: 70, right: 30, top: 20, bottom: 60 },
  xAxis: { type: "category" as const, name: "Alpha", data: alphas.value },
  yAxis: { type: "value" as const, name: props.crossValidation.metric, scale: true },
  series: [
    {
      name: "Mean score",
      type: "line" as const,
      data: props.crossValidation.path.map((point) => point.mean_score),
      // NFR-463: the three lines differ by dash pattern, not by hue alone.
      lineStyle: { type: "solid" as const, width: 2 },
    },
    {
      name: "Mean + 1 std",
      type: "line" as const,
      symbol: "none",
      data: props.crossValidation.path.map((point) => point.mean_score + point.std_score),
      lineStyle: { type: "dashed" as const, width: 1 },
    },
    {
      name: "Mean − 1 std",
      type: "line" as const,
      symbol: "none",
      data: props.crossValidation.path.map((point) => point.mean_score - point.std_score),
      lineStyle: { type: "dotted" as const, width: 1 },
    },
  ],
}));

/**
 * Exact float equality, deliberately. `CrossValidationDiagnostics` validates that
 * `selected_alpha` is a member of the path's alphas by set membership — the same exact
 * comparison — so the artifact cannot carry a selection that is merely near a scanned point.
 * A tolerance here would be looser than the contract and could mark two adjacent alphas.
 */
const pathRows = computed(() =>
  props.crossValidation.path.map((point) => [
    point.alpha,
    point.std_score,
    point.mean_score,
    point.alpha === props.crossValidation.selected_alpha ? "Selected" : "—",
  ]),
);

const foldOption = computed(() => ({
  tooltip: { trigger: "item" as const },
  grid: { left: 70, right: 30, top: 20, bottom: 50 },
  xAxis: {
    type: "category" as const,
    name: "Fold",
    data: props.crossValidation.fold_metrics.map((fold) => String(fold.fold)),
  },
  yAxis: { type: "value" as const, name: props.crossValidation.metric, scale: true },
  series: [
    {
      name: "Fold score",
      type: "scatter" as const,
      symbolSize: 12,
      data: props.crossValidation.fold_metrics.map((fold) => fold.score),
    },
  ],
}));

const foldRows = computed(() =>
  props.crossValidation.fold_metrics.map((fold) => [fold.fold, fold.rows, fold.score]),
);

const header = computed(() => [
  { name: "Method", value: props.crossValidation.method },
  { name: "Folds", value: props.crossValidation.folds },
  { name: "Seed", value: props.crossValidation.seed },
  { name: "Metric", value: props.crossValidation.metric },
  { name: "Selected alpha", value: props.crossValidation.selected_alpha },
]);
</script>

<template>
  <div>
    <table
      aria-label="Cross-validation"
      class="mt-2 w-full text-left text-sm"
    >
      <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
        <tr>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Setting
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Value
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="entry in header"
          :key="entry.name"
          class="border-b border-slate-100"
        >
          <th
            scope="row"
            class="py-1 font-normal"
          >
            {{ entry.name }}
          </th>
          <td class="py-1 tabular-nums">
            {{ entry.value }}
          </td>
        </tr>
      </tbody>
    </table>

    <ChartFigure
      title="Regularisation path"
      caption="Mean score by alpha with a ±1 std band. An alpha whose neighbours sit inside the band was not really chosen."
      :columns="['Alpha', 'Std score', 'Mean score', 'Choice']"
      :rows="pathRows"
    >
      <VChart
        class="h-80 w-full"
        :option="pathOption"
        autoresize
      />
    </ChartFigure>

    <ChartFigure
      title="Fold dispersion"
      caption="One point per fold, not their mean — FR-182 persists the dispersion because the spread is the reliability."
      :columns="['Fold', 'Rows', 'Score']"
      :rows="foldRows"
    >
      <VChart
        class="h-64 w-full"
        :option="foldOption"
        autoresize
      />
    </ChartFigure>
  </div>
</template>
