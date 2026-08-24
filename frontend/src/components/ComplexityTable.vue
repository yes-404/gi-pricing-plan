<script setup lang="ts">
import { computed } from "vue";

import type { ComplexityDiagnostic } from "@/api/diagnostics";

const props = defineProps<{ complexity: ComplexityDiagnostic }>();

/**
 * Complexity counts and ratios beside whatever thresholds are in force (FR-MODEL-81).
 *
 * The thresholds are workspace settings and are **unset by default**; there is no
 * platform-wide constant, because a large book legitimately supports a large model and
 * whether *this* model is overfitted is a judgement for the Approver with the diagnostic in
 * front of them. So an unset threshold is rendered as "none set" and the verdict column as
 * an em dash: a blank cell reads as a pass, and this table must not imply one.
 *
 * `max_factor_count` is a ceiling and `min_exposure_per_parameter` a floor, so the two are
 * compared in opposite directions. A breach shown here is not a refusal — a spec breaching a
 * set threshold is refused before any compute is spent, so this can only fire where a
 * threshold was set after the fit.
 */
const rows = computed(() => [
  {
    name: "Factor count",
    value: props.complexity.factor_count,
    threshold: props.complexity.max_factor_count,
    breached:
      props.complexity.max_factor_count != null &&
      props.complexity.factor_count > props.complexity.max_factor_count,
    direction: "above",
  },
  {
    name: "Parameter count",
    value: props.complexity.parameter_count,
    threshold: null,
    breached: false,
    direction: "above",
  },
  {
    name: "Exposure per parameter",
    value: props.complexity.exposure_per_parameter,
    threshold: props.complexity.min_exposure_per_parameter,
    breached:
      props.complexity.exposure_per_parameter != null &&
      props.complexity.min_exposure_per_parameter != null &&
      props.complexity.exposure_per_parameter < props.complexity.min_exposure_per_parameter,
    direction: "below",
  },
  {
    name: "Claims per parameter",
    value: props.complexity.claims_per_parameter,
    threshold: null,
    breached: false,
    direction: "below",
  },
]);
</script>

<template>
  <div class="mt-6">
    <table
      aria-label="Complexity"
      class="w-full text-left text-sm"
    >
      <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
        <tr>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Measure
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Value
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Threshold in force
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Against it
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="row in rows"
          :key="row.name"
          class="border-b border-slate-100"
        >
          <th
            scope="row"
            class="py-1 font-normal"
          >
            {{ row.name }}
          </th>
          <td class="py-1 tabular-nums">
            {{ row.value ?? "—" }}
          </td>
          <td class="py-1 tabular-nums">
            {{ row.threshold ?? "None set" }}
          </td>
          <td class="py-1">
            <span v-if="row.threshold == null">—</span>
            <span v-else-if="row.breached">{{ row.direction }} the threshold</span>
            <span v-else>within it</span>
          </td>
        </tr>
      </tbody>
    </table>
    <p class="mt-1 text-xs text-slate-500">
      Complexity is a diagnostic, not a verdict (FR-MODEL-81). Whether this model is
      overfitted is a judgement for the Approver with these numbers in front of them.
    </p>
  </div>
</template>
