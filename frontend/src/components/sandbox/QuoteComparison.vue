<script setup lang="ts">
/**
 * The compare panel (03 FR-262, §4.10): both results side by side, then the step differences.
 * The comparison side is summarised here and not through `QuoteOutcome`, whose heading id and
 * test id would be duplicated on the page. Rows are the response's `diff.steps` in its order;
 * nothing is re-sorted or added (RL-1765 DP-2).
 */
import type { ScoreComparison, ScoringResult, StepChange } from "@/api/score";

import { formatAmount } from "./ladder";
import { stepChangeLabel } from "./stepChange";

defineProps<{ comparison: ScoreComparison }>();

function payable(result: ScoringResult): string {
  const rung = result.premium_ladder.find((r) => r.rung === "payable_premium");
  return rung ? formatAmount(rung.value_minor) : "—";
}

function produced(side: StepChange["base"]): string {
  return side ? JSON.stringify(side.produced) : "—";
}
</script>

<template>
  <section aria-labelledby="comparison-heading">
    <h2
      id="comparison-heading"
      class="text-lg font-medium"
    >
      Compared with
      <span class="font-mono">{{ comparison.comparison.rating_version_ref }}</span>
    </h2>

    <table class="mt-3 w-full text-left text-sm">
      <caption class="sr-only">
        Both results
      </caption>
      <thead>
        <tr>
          <td />
          <th scope="col">
            Base
          </th>
          <th scope="col">
            Comparison
          </th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th scope="row">
            Version
          </th>
          <td class="font-mono">
            {{ comparison.base.rating_version_ref }}
          </td>
          <td class="font-mono">
            {{ comparison.comparison.rating_version_ref }}
          </td>
        </tr>
        <tr>
          <th scope="row">
            Outcome
          </th>
          <td>{{ comparison.base.outcome }}</td>
          <td>{{ comparison.comparison.outcome }}</td>
        </tr>
        <tr>
          <th scope="row">
            Payable premium
          </th>
          <td>{{ payable(comparison.base) }}</td>
          <td>{{ payable(comparison.comparison) }}</td>
        </tr>
      </tbody>
    </table>

    <table class="mt-6 w-full text-left text-sm">
      <caption class="mb-2 text-left text-sm text-slate-600">
        Step differences · {{ comparison.diff.unchanged }} steps unchanged for this quote
      </caption>
      <thead>
        <tr>
          <th scope="col">
            Step
          </th>
          <th scope="col">
            Change
          </th>
          <th scope="col">
            Base produced
          </th>
          <th scope="col">
            Comparison produced
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="step in comparison.diff.steps"
          :key="step.step_id"
        >
          <td>
            <span class="font-mono">{{ step.step_id }}</span>
            <span class="ml-2 text-slate-500">{{ (step.comparison ?? step.base)?.label }}</span>
          </td>
          <td>{{ stepChangeLabel(step) }}</td>
          <td class="font-mono text-xs">
            {{ produced(step.base) }}
          </td>
          <td class="font-mono text-xs">
            {{ produced(step.comparison) }}
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>
