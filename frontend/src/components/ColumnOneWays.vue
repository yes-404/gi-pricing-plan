<script setup lang="ts">
/**
 * The candidate rating columns, each with the one-way the Profile already carries
 * (`02` §5.3, `01` FR-61).
 *
 * **Read, never computed.** FR-61 says these "are computed once, here" — in the
 * profiling pass — so the browser renders what the artifact stores and derives nothing.
 * (FR-62 says a Profile is never recomputed on request, which is the wider claim; the
 * tighter one is what binds this component.)
 *
 * **The incurred amount is deliberately absent, and this is not a styling choice.**
 * `OneWayRow.claim_amount_minor` is money in minor units *of the workspace currency*, and
 * this view cannot reach that currency: it holds a `dataset_version_id`, `DatasetVersion`
 * carries no currency, and `/datasets/{dataset_id}` is **PATCH-only** — there is no GET by
 * id — so the only route to `Dataset.currency` needs a slug the view does not have.
 * Rendering the number without a symbol would be a bare integer of minor units, and
 * guessing `GBP` is what `OQ-551` exists to stop: a euro amount under a pound sign is a
 * wrong number that looks like a right one.
 *
 * Everything else needs no currency. Exposure, claim counts and frequency are dimensionless
 * or in years; `mean_severity` and `mean_burning_cost` are **statistics** in minor units,
 * not amounts (FR-64 renamed them off `_minor` for exactly that reason), and W6b-3
 * established rendering them as scaled statistics rather than as money.
 *
 * So the omission costs one column of a volume measure the exposure column already conveys,
 * and it is stated here rather than left for a reader to notice.
 */
import type { OneWaySummary } from "@/api/profiles";
import { formatDecimalString } from "@/api/versions";

defineProps<{ oneWays: readonly OneWaySummary[] }>();

/** An interval as one cell, or `—`. Scaled where the statistic it belongs to is. */
function interval(
  ci: readonly [number, number] | null | undefined,
  digits: number,
  scale = 1,
): string | null {
  if (ci == null) return null;
  return `${(ci[0] / scale).toFixed(digits)}–${(ci[1] / scale).toFixed(digits)}`;
}
</script>

<template>
  <section>
    <h2 class="mb-2 text-sm font-medium text-slate-700">
      Candidate columns
    </h2>

    <p
      v-if="!oneWays.length"
      class="text-sm text-slate-500"
    >
      This version's profile records no one-ways.
    </p>

    <details
      v-for="summary in oneWays"
      :key="summary.column"
      class="mb-2 rounded-md border border-slate-200"
    >
      <summary class="cursor-pointer px-3 py-2 text-sm font-medium">
        {{ summary.column }}
        <span class="ml-2 font-normal text-slate-500">
          {{ (summary.rows ?? []).length }} levels
        </span>
      </summary>

      <div class="overflow-x-auto px-3 pb-3">
        <table class="w-full text-left text-sm">
          <caption class="sr-only">
            One-way summary for {{ summary.column }}
          </caption>
          <thead class="border-b border-slate-200 text-xs uppercase text-slate-500">
            <tr>
              <th
                scope="col"
                class="py-1 font-medium"
              >
                Level
              </th>
              <th
                scope="col"
                class="py-1 font-medium"
              >
                Exposure
              </th>
              <th
                scope="col"
                class="py-1 font-medium"
              >
                Claims
              </th>
              <th
                scope="col"
                class="py-1 font-medium"
              >
                Frequency
              </th>
              <th
                scope="col"
                class="py-1 font-medium"
              >
                Frequency CI
              </th>
              <th
                scope="col"
                class="py-1 font-medium"
              >
                Severity
              </th>
              <th
                scope="col"
                class="py-1 font-medium"
              >
                Burning cost
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in summary.rows ?? []"
              :key="row.level"
              class="border-b border-slate-100"
            >
              <td class="py-1">
                {{ row.level }}
              </td>
              <td class="py-1 tabular-nums">
                {{ formatDecimalString(row.exposure_years) }}
              </td>
              <td class="py-1 tabular-nums">
                {{ row.claim_count.toLocaleString() }}
              </td>
              <td class="py-1 tabular-nums">
                {{ row.frequency?.toFixed(4) ?? "—" }}
              </td>
              <td class="py-1 tabular-nums">
                {{ interval(row.frequency_ci, 4) ?? "—" }}
              </td>
              <td class="py-1 tabular-nums">
                {{ row.mean_severity == null ? "—" : (row.mean_severity / 100).toFixed(2) }}
              </td>
              <td class="py-1 tabular-nums">
                {{ row.mean_burning_cost == null
                  ? "—" : (row.mean_burning_cost / 100).toFixed(2) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </details>
  </section>
</template>
