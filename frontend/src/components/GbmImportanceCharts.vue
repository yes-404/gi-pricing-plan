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
  PermutationOmission,
} from "@/api/diagnostics";
import type { Column } from "@/chart-table";
import ChartFigure from "@/components/ChartFigure.vue";

use([BarChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

const props = defineProps<{
  importances: readonly FeatureImportance[];
  permutationImportances: readonly PermutationImportance[];
  permutationOmitted?: readonly PermutationOmission[];
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

const gainColumns: readonly Column<FeatureImportance>[] = [
  { key: "feature", label: "Feature", value: (i) => i.feature },
  { key: "cover", label: "Cover", value: (i) => i.cover ?? null },
  { key: "frequency", label: "Frequency", value: (i) => i.frequency },
  { key: "gain", label: "Gain", value: (i) => i.gain },
];

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

const permutationColumns: readonly Column<PermutationImportance>[] = [
  { key: "feature", label: "Feature", value: (i) => i.feature },
  { key: "baseline", label: "Baseline", value: (i) => i.baseline },
  { key: "permuted", label: "Permuted", value: (i) => i.permuted },
  { key: "repeats", label: "Repeats", value: (i) => i.repeats },
  { key: "seed", label: "Seed", value: (i) => i.seed },
  { key: "degradation", label: "Degradation", value: (i) => i.degradation },
];

/**
 * Why a factor has no permutation importance, in words (FR-178). An unrecognised reason is
 * shown under its own name, not a default.
 */
function omissionReason(reason: string): string {
  if (reason === "operand_of_interaction") {
    return "it is, or shares a column with, an operand of an interaction, so it cannot be shuffled alone (the interaction is shuffled jointly)";
  }
  if (reason === "no_holdout_column") {
    return "the holdout has no column for it";
  }
  return reason;
}

const omissionNotes = computed(() =>
  (props.permutationOmitted ?? []).map(
    (omission) => `${omission.feature}: not measured — ${omissionReason(omission.reason)}.`,
  ),
);

const sharedColumnNotes = computed(() =>
  props.permutationImportances
    .filter((importance) => (importance.shared_source_columns ?? []).length > 0)
    .map(
      (importance) =>
        `${importance.feature}: shuffling also moved ${(importance.shared_source_columns ?? []).join(", ")}, which another factor draws on, so its degradation is the joint effect.`,
    ),
);
</script>

<template>
  <div>
    <ChartFigure
      title="Feature importance"
      caption="Gain, with cover and frequency beside it. A property of the fitted booster — there is no train or holdout split to report."
      :columns="gainColumns"
      :rows="importances"
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
      :columns="permutationColumns"
      :rows="permutationImportances"
    >
      <VChart
        class="h-80 w-full"
        :option="permutationOption"
        autoresize
      />
    </ChartFigure>

    <ul
      v-if="omissionNotes.length"
      aria-label="Permutation omissions"
      class="mt-2 text-sm text-slate-600"
    >
      <li
        v-for="note in omissionNotes"
        :key="note"
      >
        {{ note }}
      </li>
    </ul>

    <ul
      v-if="sharedColumnNotes.length"
      aria-label="Shared source columns"
      class="mt-2 text-sm text-slate-600"
    >
      <li
        v-for="note in sharedColumnNotes"
        :key="note"
      >
        {{ note }}
      </li>
    </ul>

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
