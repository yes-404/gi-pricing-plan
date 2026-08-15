<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { RouterLink } from "vue-router";

import { ProblemError, isProblem } from "@/api/problem";
import {
  getOneWay,
  getProfile,
  psiBand,
  type OneWaySummary,
  type Profile,
} from "@/api/profiles";
import { formatDecimalString, formatMinor, getVersion } from "@/api/versions";
import OneWayChart from "@/components/OneWayChart.vue";

const props = defineProps<{ slug: string; version: string; currency?: string }>();

const profile = ref<Profile | null>(null);
const selected = ref<string | null>(null);
const oneWay = ref<OneWaySummary | null>(null);
const oneWayMissing = ref(false);
const loading = ref(true);
const problem = ref<ProblemError | null>(null);
const versionId = ref<string | null>(null);

const currency = computed(() => props.currency ?? "GBP");
const rateable = computed(() => (profile.value?.one_ways ?? []).map((o) => o.column));

async function load(): Promise<void> {
  loading.value = true;
  problem.value = null;
  try {
    const version = await getVersion(props.slug, Number(props.version));
    versionId.value = version.id;
    profile.value = await getProfile(version.id);
    selected.value = rateable.value[0] ?? null;
  } catch (error) {
    if (error instanceof ProblemError) problem.value = error;
    else throw error;
  } finally {
    loading.value = false;
  }
}

watch(selected, async (column) => {
  oneWay.value = null;
  oneWayMissing.value = false;
  if (!column || !versionId.value) return;
  try {
    oneWay.value = await getOneWay(versionId.value, column);
  } catch (error) {
    // FR-DATA-27: a column with no *stored* one-way is an answer, not a failure. The
    // platform refuses to compute one on request, and so does this.
    if (isProblem(error, "NOT_FOUND")) oneWayMissing.value = true;
    else throw error;
  }
});

onMounted(() => void load());

const PSI_TONE: Record<string, string> = {
  stable: "text-slate-500",
  shifted: "text-amber-700 font-medium",
  broken: "text-red-700 font-medium",
};
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
        <span class="mx-1.5">/</span>{{ slug }}<span class="mx-1.5">/</span>
        <RouterLink
          :to="`/data/${slug}/v/${version}`"
          class="hover:underline"
        >
          v{{ version }}
        </RouterLink>
      </p>
      <h1 class="mt-1 text-xl font-semibold tracking-tight">
        Profile
      </h1>
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

    <template v-else-if="profile">
      <p class="text-sm text-slate-600 tabular-nums">
        {{ profile.row_count.toLocaleString() }} rows ·
        {{ (profile.columns ?? []).length }} columns ·
        {{ rateable.length }} candidate rating factors
      </p>

      <section
        v-if="rateable.length"
        class="mt-6"
      >
        <div class="flex items-center gap-3">
          <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
            One-way
          </h2>
          <select
            v-model="selected"
            aria-label="Rating factor"
            class="rounded-md border border-slate-300 px-2 py-1 text-sm"
          >
            <option
              v-for="column in rateable"
              :key="column"
              :value="column"
            >
              {{ column }}
            </option>
          </select>
        </div>

        <p
          v-if="oneWayMissing"
          class="mt-3 text-sm text-slate-500"
        >
          No stored one-way for this column. FR-DATA-27 reads them from the Profile and
          never computes one on request.
        </p>
        <template v-else-if="oneWay">
          <OneWayChart
            :summary="oneWay"
            class="mt-3"
          />
          <table class="mt-3 w-full text-left text-sm">
            <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th
                  scope="col"
                  class="py-2 font-medium"
                >
                  Level
                </th>
                <th
                  scope="col"
                  class="py-2 text-right font-medium"
                >
                  Exposure
                </th>
                <th
                  scope="col"
                  class="py-2 text-right font-medium"
                >
                  Claims
                </th>
                <th
                  scope="col"
                  class="py-2 text-right font-medium"
                >
                  Incurred
                </th>
                <th
                  scope="col"
                  class="py-2 text-right font-medium"
                >
                  Frequency
                </th>
                <th
                  scope="col"
                  class="py-2 text-right font-medium"
                >
                  Severity
                </th>
                <th
                  scope="col"
                  class="py-2 text-right font-medium"
                >
                  Burning cost
                </th>
              </tr>
            </thead>
            <tbody class="tabular-nums">
              <tr
                v-for="row in oneWay.rows"
                :key="row.level"
                class="border-b border-slate-100"
              >
                <td class="py-2 font-medium">
                  {{ row.level }}
                </td>
                <!-- Exact decimal, formatted from the string and never parsed. -->
                <td class="py-2 text-right">
                  {{ formatDecimalString(row.exposure_years) }}
                </td>
                <td class="py-2 text-right">
                  {{ row.claim_count.toLocaleString() }}
                </td>
                <!-- The one `_minor` field on this row that is an exact amount. -->
                <td class="py-2 text-right">
                  {{ formatMinor(row.claim_amount_minor, currency) }}
                </td>
                <td class="py-2 text-right">
                  {{ row.frequency?.toFixed(4) ?? "—" }}
                </td>
                <!-- `severity_minor` and `burning_cost_minor` end in `_minor` and are
                     **float ratios**, not amounts: amount ÷ claims and amount ÷ exposure.
                     Formatting them as currency would imply an exactness they do not have,
                     so they are shown as the statistics they are. -->
                <td class="py-2 text-right">
                  {{ row.severity_minor == null ? "—" : (row.severity_minor / 100).toFixed(2) }}
                </td>
                <td class="py-2 text-right">
                  {{ row.burning_cost_minor == null ? "—" : (row.burning_cost_minor / 100).toFixed(2) }}
                </td>
              </tr>
            </tbody>
          </table>
        </template>
      </section>

      <section class="mt-8">
        <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Columns
        </h2>
        <div class="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <article
            v-for="column in profile.columns"
            :key="column.name"
            class="rounded-md border border-slate-200 p-3"
          >
            <header class="flex items-baseline gap-2">
              <h3 class="font-mono text-sm font-medium">
                {{ column.name }}
              </h3>
              <span class="text-xs text-slate-500">{{ column.semantic_type }}</span>
              <span
                :class="['ml-auto text-xs', PSI_TONE[psiBand(null)]]"
              >{{ column.dtype }}</span>
            </header>
            <dl class="mt-2 grid grid-cols-2 gap-x-3 gap-y-1 text-xs tabular-nums">
              <dt class="text-slate-500">
                distinct
              </dt>
              <dd>{{ column.distinct_count.toLocaleString() }}</dd>
              <dt class="text-slate-500">
                nulls
              </dt>
              <dd>{{ (column.null_rate * 100).toFixed(2) }}%</dd>
              <template v-if="column.mean != null">
                <dt class="text-slate-500">
                  mean
                </dt>
                <dd>{{ column.mean.toFixed(3) }}</dd>
                <dt class="text-slate-500">
                  range
                </dt>
                <dd>{{ column.minimum }} – {{ column.maximum }}</dd>
              </template>
            </dl>
            <ul
              v-if="(column.top_levels ?? []).length"
              class="mt-2 flex flex-wrap gap-1"
            >
              <li
                v-for="[level, count] in (column.top_levels ?? []).slice(0, 6)"
                :key="level"
                class="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-xs text-slate-700"
              >
                {{ level }} · {{ count.toLocaleString() }}
              </li>
            </ul>
          </article>
        </div>
      </section>
    </template>
  </section>
</template>
