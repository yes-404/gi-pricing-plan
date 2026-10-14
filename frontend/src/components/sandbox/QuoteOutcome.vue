<script setup lang="ts">
/**
 * What a scored quote came to: its outcome, a decline's reasons, the declared outputs, and
 * the per-peril line (03 FR-256, FR-249).
 *
 * A declined quote is a successful result (FR-256): its reasons are listed, plural, and the
 * ladder still renders beside it because `premium_ladder` is populated through to
 * `payable_premium` for every outcome. **Per-peril components are shown as absent**
 * (FR-249, R6.1, `RL-1459`, `OQ-1460`): no producer exists, so this says so rather than
 * building a view with nothing behind it.
 */
import type { ScoringResult } from "@/api/score";

defineProps<{ result: ScoringResult }>();
</script>

<template>
  <section aria-labelledby="outcome-heading">
    <h2
      id="outcome-heading"
      class="text-lg font-medium"
    >
      Outcome:
      <span
        data-testid="outcome"
        :class="result.outcome === 'declined' ? 'text-amber-700' : 'text-slate-900'"
      >{{ result.outcome }}</span>
    </h2>

    <div
      v-if="result.outcome === 'declined'"
      class="mt-2 rounded-md border border-amber-200 bg-amber-50 p-3"
    >
      <p class="text-sm font-medium text-amber-800">
        Declined — the ladder below is what the quote would have cost.
      </p>
      <ul
        aria-label="Decline reasons"
        class="mt-1 list-disc pl-5 font-mono text-sm text-amber-800"
      >
        <li
          v-for="reason in result.decline_reasons ?? []"
          :key="reason"
        >
          {{ reason }}
        </li>
      </ul>
    </div>

    <dl
      v-if="Object.keys(result.outputs ?? {}).length > 0"
      class="mt-3 grid grid-cols-[14rem_1fr] gap-x-3 gap-y-1 text-sm"
      aria-label="Outputs"
    >
      <template
        v-for="(value, name) in result.outputs"
        :key="name"
      >
        <dt class="font-mono text-slate-500">
          {{ name }}
        </dt>
        <dd class="font-mono">
          {{ JSON.stringify(value) }}
        </dd>
      </template>
    </dl>

    <p
      data-testid="per-peril-absent"
      class="mt-3 text-xs text-slate-500"
    >
      Per-peril risk premium components: not available. No step produces them yet
      (FR-249, open question OQ-1460).
    </p>
  </section>
</template>
