<script setup lang="ts">
import type { ComparisonMetric, MetricDirection } from "@/api/comparisons";
import { leaderState } from "@/api/comparisons";
import ModelRefLink from "@/components/ModelRefLink.vue";

const props = defineProps<{
  metrics: readonly ComparisonMetric[];
  modelRefs: readonly string[];
}>();

const DIRECTION_LABEL: Record<MetricDirection, string> = {
  higher_is_better: "higher is better",
  lower_is_better: "lower is better",
  closer_to_one_is_better: "closer to 1 is better",
  not_ordered: "not ordered",
};

/**
 * The metric's value for one model, or `undefined` when the metric does not carry that model
 * at all. §4.11 makes that impossible on a well-formed artifact — every metric carries a
 * value for every model — so it renders as an em dash distinct from the `n/a` a stored null
 * gets, and the difference is the difference between "nobody measured" and "does not apply".
 */
function valueFor(metric: ComparisonMetric, modelRef: string): number | null | undefined {
  return metric.values.find((v) => v.model_ref === modelRef)?.value;
}

function format(value: number | null | undefined): string {
  if (value === undefined) return "—";
  if (value === null) return "n/a";
  // Integral values are counts (§4.11's `rows` is 169503.0) and reading "169503.0000" as a
  // measurement is worse than reading it as a count.
  return Number.isInteger(value) ? String(value) : value.toFixed(4);
}
</script>

<template>
  <table
    class="mt-2 w-full text-left text-sm"
    aria-label="Aligned metrics"
  >
    <thead>
      <tr class="border-b border-slate-200">
        <th
          scope="col"
          class="py-2 font-medium"
        >
          Metric
        </th>
        <th
          scope="col"
          class="py-2 font-medium"
        >
          Direction
        </th>
        <th
          v-for="ref in props.modelRefs"
          :key="ref"
          scope="col"
          class="py-2 font-medium"
        >
          <ModelRefLink :model-ref="ref" />
        </th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="metric in props.metrics"
        :key="metric.metric"
        class="border-b border-slate-100"
      >
        <th
          scope="row"
          class="py-2 font-mono text-xs font-normal"
        >
          {{ metric.metric }}
        </th>
        <td class="py-2 text-xs text-slate-500">
          {{ DIRECTION_LABEL[metric.direction] }}
          <span
            v-if="metric.direction === 'not_ordered'"
            class="ml-1 rounded bg-slate-100 px-1 py-0.5 text-slate-600"
          >not ranked</span>
          <span
            v-else-if="metric.leader === null || metric.leader === undefined"
            class="ml-1 rounded bg-slate-100 px-1 py-0.5 text-slate-600"
          >tied</span>
        </td>
        <td
          v-for="ref in props.modelRefs"
          :key="ref"
          class="py-2 font-mono text-xs"
          :class="leaderState(metric, ref) === 'leader' ? 'font-semibold text-teal-800' : ''"
        >
          {{ format(valueFor(metric, ref)) }}
          <span
            v-if="leaderState(metric, ref) === 'leader'"
            class="ml-1 not-italic"
            aria-label="leads this metric"
            title="Leads this metric"
          >★</span>
        </td>
      </tr>
    </tbody>
  </table>
</template>
