<script setup lang="ts">
import { BarChart } from "echarts/charts";
import { GridComponent, LegendComponent, TooltipComponent } from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { computed } from "vue";
import VChart from "vue-echarts";

import type {
  FeatureImportance,
  MonotonicityCheck,
  PermutationImportance,
} from "@/api/diagnostics";
import ChartFigure from "@/components/ChartFigure.vue";

use([BarChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

const props = defineProps<{
  importances: readonly FeatureImportance[];
  permutationImportances: readonly PermutationImportance[];
  monotonicity: readonly MonotonicityCheck[];
}>();

/**
 * Split importance — gain, cover and frequency (FR-174).
 *
 * Unpartitioned: an importance is a property of the fitted booster, counted over its own
 * splits rather than measured against a population of rows, so there is no train and no
 * holdout to report (FR-183, as scoped 2026-08-24). `cover` is nullable — LightGBM does
 * not report it — and a null is shown as a null rather than as a zero, which would read as
 * "this feature covered nothing".
 */
const gainOption = computed(() => ({
  tooltip: { trigger: "axis" as const },
  grid: { left: 140, right: 30, top: 20, bottom: 40 },
  xAxis: { type: "value" as const, name: "Gain" },
  yAxis: {
    type: "category" as const,
    data: props.importances.map((importance) => importance.feature).reverse(),
  },
  series: [
    {
      name: "Gain",
      type: "bar" as const,
      data: props.importances.map((importance) => importance.gain).reverse(),
    },
  ],
}));

const gainRows = computed(() =>
  props.importances.map((importance) => [
    importance.feature,
    importance.cover ?? null,
    importance.frequency,
    importance.gain,
  ]),
);

/**
 * Permutation importance, **on the holdout** (FR-174).
 *
 * Single-valued, and labelled as holdout rather than rendered opposite an empty train column.
 * It is not a property of the fit — it *is* computed over rows — but its `degradation` is
 * degradation of the holdout metric, so a train counterpart would answer a different
 * question. The contract carries no train field for it, and a view that showed one would show
 * a column nothing can fill.
 *
 * `repeats` and `seed` travel with the number because a degradation from five shuffles under
 * a recorded seed is reproducible and one without them is an anecdote.
 */
const permutationOption = computed(() => ({
  tooltip: { trigger: "axis" as const },
  grid: { left: 140, right: 30, top: 20, bottom: 40 },
  xAxis: { type: "value" as const, name: "Degradation" },
  yAxis: {
    type: "category" as const,
    data: props.permutationImportances.map((importance) => importance.feature).reverse(),
  },
  series: [
    {
      name: "Degradation",
      type: "bar" as const,
      data: props.permutationImportances.map((importance) => importance.degradation).reverse(),
    },
  ],
}));

const permutationRows = computed(() =>
  props.permutationImportances.map((importance) => [
    importance.feature,
    importance.baseline,
    importance.permuted,
    importance.repeats,
    importance.seed,
    importance.degradation,
  ]),
);
</script>

<template>
  <div>
    <ChartFigure
      title="Feature importance"
      caption="Gain, with cover and frequency beside it. A property of the fitted booster — there is no train or holdout split to report."
      :columns="['Feature', 'Cover', 'Frequency', 'Gain']"
      :rows="gainRows"
    >
      <VChart
        class="h-80 w-full"
        :option="gainOption"
        autoresize
      />
    </ChartFigure>

    <ChartFigure
      title="Permutation importance (holdout)"
      caption="How much the holdout metric degrades when one feature is shuffled. Measured on the holdout by definition, so there is no train counterpart."
      :columns="['Feature', 'Baseline', 'Permuted', 'Repeats', 'Seed', 'Degradation']"
      :rows="permutationRows"
    >
      <VChart
        class="h-80 w-full"
        :option="permutationOption"
        autoresize
      />
    </ChartFigure>

    <!-- FR-174: monotonicity verification is that the fitted response actually respects
         the declared constraint, so "declared" and "holds" are read together — a factor with
         no declared direction cannot violate one. The word is what carries the verdict:
         `worst_violation` defaults to `0.0` and is `0.0` whenever the constraint holds, so
         the magnitude column on its own cannot tell a clean factor from a breached one. -->
    <table
      aria-label="Monotonicity"
      class="mt-6 w-full text-left text-sm"
    >
      <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
        <tr>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Factor
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Declared
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Worst violation
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="check in monotonicity"
          :key="check.factor"
          class="border-b border-slate-100"
        >
          <th
            scope="row"
            class="py-1 font-normal"
          >
            {{ check.factor }}
          </th>
          <td class="py-1">
            {{ check.declared }} — {{ check.holds ? "holds" : "violated" }}
          </td>
          <td class="py-1 tabular-nums">
            {{ check.worst_violation }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
