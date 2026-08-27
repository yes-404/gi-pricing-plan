<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";

import { getDataset, type Dataset } from "@/api/datasets";
import { isProblem, ProblemError } from "@/api/problem";
import {
  formatDecimalString,
  formatMinor,
  getRejected,
  getVersion,
  type DatasetVersion,
  type RejectedRows,
} from "@/api/versions";

const props = defineProps<{ slug: string; version: string }>();

const detail = ref<DatasetVersion | null>(null);
/** The dataset this version belongs to — its currency is what amounts are denominated
 *  in. The empty string is unreachable at render: the value is read only inside the
 *  loaded branch, where `getDataset` has set it. It exists to keep `formatMinor`'s
 *  required-`string` signature honest, not as a money default (OQ-OVR-14 (b)). */
const dataset = ref<Dataset | null>(null);
const rejected = ref<RejectedRows | null>(null);
/** Distinct from "not loaded": a derived version has no run of its own, and that is an
 *  answer rather than a failure. */
const hasNoRun = ref(false);
const loading = ref(true);
const problem = ref<ProblemError | null>(null);

const currency = computed(() => dataset.value?.currency ?? "");
const tables = computed(() => detail.value?.tables ?? []);

const STATUS_TONE: Record<string, string> = {
  draft: "bg-slate-100 text-slate-700",
  validating: "bg-amber-100 text-amber-900",
  validated: "bg-emerald-100 text-emerald-900",
  archived: "bg-slate-200 text-slate-600",
};

async function load(): Promise<void> {
  loading.value = true;
  problem.value = null;
  try {
    const loaded = await getVersion(props.slug, Number(props.version));
    detail.value = loaded;
    dataset.value = await getDataset(props.slug);
    try {
      rejected.value = await getRejected(loaded.id);
    } catch (error) {
      // FR-DATA-7: a derived version has no ingestion run. Not an error to show.
      if (isProblem(error, "NOT_FOUND")) hasNoRun.value = true;
      else throw error;
    }
  } catch (error) {
    if (error instanceof ProblemError) problem.value = error;
    else throw error;
  } finally {
    loading.value = false;
  }
}

onMounted(() => void load());
</script>

<template>
  <section>
    <header class="mb-5">
      <p class="text-sm text-slate-500">
        <RouterLink
          to="/data"
          class="hover:underline"
        >
          Datasets
        </RouterLink>
        <span class="mx-1.5">/</span>{{ slug }}
      </p>
      <div class="mt-1 flex items-center gap-3">
        <h1 class="text-xl font-semibold tracking-tight">
          Version {{ version }}
        </h1>
        <span
          v-if="detail"
          :class="['rounded px-2 py-0.5 text-xs font-medium uppercase tracking-wide',
                   STATUS_TONE[detail.status] ?? 'bg-slate-100']"
        >{{ detail.status }}</span>
      </div>
    </header>

    <p
      v-if="loading"
      class="text-sm text-slate-500"
    >
      Loading…
    </p>

    <div
      v-else-if="problem"
      role="alert"
      class="rounded-md border border-red-200 bg-red-50 p-4"
    >
      <p class="font-medium text-red-900">
        {{ problem.problem.title }}
      </p>
      <p
        v-if="problem.problem.detail"
        class="mt-1 text-sm text-red-800"
      >
        {{ problem.problem.detail }}
      </p>
      <p
        v-if="problem.traceId"
        class="mt-2 font-mono text-xs text-red-700"
      >
        trace {{ problem.traceId }}
      </p>
    </div>

    <template v-else-if="detail">
      <div class="flex flex-wrap gap-3">
        <RouterLink
          :to="`/data/${slug}/v/${detail.version}/validation`"
          class="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50"
        >
          Validation report
        </RouterLink>
        <!--
          The way into `02` §5.3's factor workbench. Shown only on a `validated` version,
          because that is the only kind the platform will propose a banding against (`02`
          R1) — offering the link on a draft would send the actuary to a 409.
        -->
        <RouterLink
          v-if="detail.status === 'validated'"
          :to="`/factors/${detail.id}`"
          class="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50"
        >
          Factor workbench
        </RouterLink>
        <RouterLink
          :to="`/data/${slug}/v/${detail.version}/profile`"
          class="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50"
        >
          Profile
        </RouterLink>
      </div>

      <section
        v-if="detail.totals"
        class="mt-6"
      >
        <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Totals
        </h2>
        <dl class="mt-2 flex flex-wrap gap-x-10 gap-y-3">
          <div>
            <dt class="text-xs text-slate-500">
              Exposure
            </dt>
            <!-- Formatted from the string, never parsed: a JS number is a float64 and the
                 backend already summed this exactly (FR-OVR-7). -->
            <dd class="text-lg font-medium tabular-nums">
              {{ formatDecimalString(detail.totals.exposure_years) }}
              <span class="text-sm font-normal text-slate-500">years</span>
            </dd>
          </div>
          <div>
            <dt class="text-xs text-slate-500">
              Claims
            </dt>
            <dd class="text-lg font-medium tabular-nums">
              {{ detail.totals.claim_count.toLocaleString() }}
            </dd>
          </div>
          <div>
            <dt class="text-xs text-slate-500">
              Incurred
            </dt>
            <dd class="text-lg font-medium tabular-nums">
              {{ formatMinor(detail.totals.claim_amount_minor, currency) }}
            </dd>
          </div>
        </dl>
      </section>

      <section class="mt-8">
        <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Tables — {{ tables.length }}
        </h2>
        <article
          v-for="table in tables"
          :key="table.name"
          class="mt-3 rounded-md border border-slate-200 p-4"
        >
          <header class="flex items-baseline gap-3">
            <h3 class="font-mono text-sm font-medium">
              {{ table.name }}
            </h3>
            <span class="text-xs text-slate-500 tabular-nums">
              {{ table.row_count.toLocaleString() }} rows
            </span>
            <span
              v-if="table.primary_key?.length"
              class="text-xs text-slate-500"
            >
              key: {{ table.primary_key.join(", ") }}
            </span>
            <span
              v-if="table.blob"
              class="ml-auto font-mono text-xs text-slate-400"
            >
              {{ (table.blob.bytes / 1e6).toFixed(1) }} MB
            </span>
          </header>

          <details class="mt-3">
            <summary class="cursor-pointer text-xs text-slate-600">
              Schema ({{ Object.keys(table.arrow_schema ?? {}).length }} columns)
            </summary>
            <table class="mt-2 w-full text-left text-xs">
              <thead class="text-slate-500">
                <tr>
                  <th
                    scope="col"
                    class="py-1 font-medium"
                  >
                    Column
                  </th>
                  <th
                    scope="col"
                    class="py-1 font-medium"
                  >
                    Type
                  </th>
                  <th
                    scope="col"
                    class="py-1 font-medium"
                  >
                    Source header
                  </th>
                </tr>
              </thead>
              <tbody class="font-mono">
                <tr
                  v-for="(dtype, column) in table.arrow_schema"
                  :key="column"
                  class="border-t border-slate-100"
                >
                  <td class="py-1">
                    {{ column }}
                  </td>
                  <td class="py-1 text-slate-600">
                    {{ dtype }}
                  </td>
                  <!-- FR-DATA-5. Normalisation is lossy: freMTPL2's `IDpol` becomes
                       `i_dpol`, and without the original a user cannot tell which of their
                       columns a rule is talking about. -->
                  <td class="py-1 text-slate-500">
                    {{ table.source_names?.[column] ?? "—" }}
                  </td>
                </tr>
              </tbody>
            </table>
          </details>
        </article>
      </section>

      <section class="mt-8">
        <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Rejected rows
        </h2>
        <p
          v-if="hasNoRun"
          class="mt-2 text-sm text-slate-500"
        >
          This version was derived from another, so it has no ingestion run of its own.
        </p>
        <template v-else-if="rejected">
          <p class="mt-2 text-sm tabular-nums text-slate-700">
            {{ rejected.rows_rejected.toLocaleString() }} of
            {{ rejected.rows_read.toLocaleString() }} rows quarantined
            ({{ (rejected.reject_rate * 100).toFixed(3) }}%)
          </p>
          <p
            v-if="rejected.rows_rejected === 0"
            class="mt-1 text-sm text-slate-500"
          >
            Every row was accepted.
          </p>
          <details
            v-else
            class="mt-2"
          >
            <summary class="cursor-pointer text-xs text-slate-600">
              Sample ({{ rejected.sample.length }})
            </summary>
            <ul class="mt-1 max-h-56 overflow-y-auto font-mono text-xs text-slate-700">
              <li
                v-for="(row, index) in rejected.sample"
                :key="index"
                class="border-t border-slate-100 py-1"
              >
                {{ JSON.stringify(row) }}
              </li>
            </ul>
          </details>
        </template>
      </section>
    </template>
  </section>
</template>
