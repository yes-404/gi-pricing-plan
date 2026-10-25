<script setup lang="ts">
/**
 * The largest movers (03 FR-263): the run's movers in §4.6's order, each row expandable to its
 * individual quote's portfolio columns (the drill-down). The rows are the generated
 * `DislocationMover`; the portfolio columns are `columns`, joined at read (NFR-499).
 */
import { ref } from "vue";

import type { DislocationMover } from "@/api/dislocationRuns";

import { formatMinor } from "./format";

defineProps<{ movers: readonly DislocationMover[] }>();

const open = ref<ReadonlySet<string>>(new Set());

function toggle(quoteId: string): void {
  const next = new Set(open.value);
  if (next.has(quoteId)) next.delete(quoteId);
  else next.add(quoteId);
  open.value = next;
}

/** `change_pct` is a decimal string, shown as the platform sent it. */
function pct(mover: DislocationMover): string {
  return `${mover.change_pct}%`;
}
</script>

<template>
  <section class="mt-6">
    <h3 class="text-sm font-semibold text-slate-700">
      Largest movers
    </h3>
    <p class="mt-1 text-xs text-slate-500">
      Policies whose change is at or beyond the run's threshold, largest first. Amounts are in
      major units; currency not configured (OQ-551).
    </p>
    <p
      v-if="movers.length === 0"
      class="mt-2 text-sm text-slate-500"
    >
      No policy moved beyond the threshold.
    </p>
    <table
      v-else
      aria-label="Largest movers"
      class="mt-2 w-full text-left text-sm"
    >
      <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
        <tr>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Quote
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Baseline
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Candidate
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Change
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Change %
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Origin rung
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Detail
          </th>
        </tr>
      </thead>
      <tbody>
        <template
          v-for="mover in movers"
          :key="mover.quote_id"
        >
          <tr class="border-b border-slate-100">
            <th
              scope="row"
              class="py-1 font-mono font-normal"
            >
              {{ mover.quote_id }}
            </th>
            <td class="py-1 tabular-nums">
              {{ formatMinor(mover.baseline_minor) }}
            </td>
            <td class="py-1 tabular-nums">
              {{ formatMinor(mover.candidate_minor) }}
            </td>
            <td class="py-1 tabular-nums">
              {{ formatMinor(mover.change_minor) }}
            </td>
            <td class="py-1 tabular-nums">
              {{ pct(mover) }}
            </td>
            <td class="py-1">
              {{ mover.origin_rung ?? "—" }}
            </td>
            <td class="py-1">
              <button
                type="button"
                class="text-sm text-blue-700 hover:underline"
                :aria-expanded="open.has(mover.quote_id)"
                :aria-controls="`mover-${mover.quote_id}`"
                @click="toggle(mover.quote_id)"
              >
                {{ open.has(mover.quote_id) ? "Hide" : "Show" }} quote {{ mover.quote_id }}
              </button>
            </td>
          </tr>
          <tr
            v-if="open.has(mover.quote_id)"
            :id="`mover-${mover.quote_id}`"
            class="border-b border-slate-100 bg-slate-50"
          >
            <td colspan="7">
              <dl class="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 py-2 text-sm">
                <template
                  v-for="(value, name) in mover.columns"
                  :key="name"
                >
                  <dt class="text-slate-500">
                    {{ name }}
                  </dt>
                  <dd>{{ value ?? "—" }}</dd>
                </template>
              </dl>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </section>
</template>
