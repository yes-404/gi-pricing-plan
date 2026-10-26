<script setup lang="ts">
/**
 * The Regression suite view (03 §5.3, FR-1932): `/rating/:slug/v/:version/tests`. `:slug` and
 * `:version` are the Rating Version's own (RL-1473). It lists the version's runs newest first,
 * opens the newest by default, honours `?run=<id>`, and marks the run the version's
 * `evidence.regression_suite_run_id` names. It is read-only: it starts no run (RL-1900
 * DP-S11-2), and it reads a run by id, never the case log or `/blobs` (FR-1221).
 */
import { computed, onMounted, ref, watch } from "vue";
import { RouterLink, useRouter } from "vue-router";

import { ProblemError } from "@/api/problem";
import {
  getRegressionRun,
  listRegressionRuns,
  type RegressionRun,
  type RegressionRunSummary,
} from "@/api/regressionRuns";
import { getRatingVersionByRef, type RatingVersion } from "@/api/ratingVersions";
import { formatMinor } from "@/components/dislocation/format";

const props = defineProps<{ slug: string; version: string; run?: string }>();
const router = useRouter();

const rating = ref<RatingVersion | null>(null);
const runs = ref<RegressionRunSummary[]>([]);
const truncated = ref(false);
const result = ref<RegressionRun | null>(null);
const loading = ref(true);
const problem = ref<ProblemError | null>(null);

const heading = computed(() => `${props.slug}@${props.version}`);
const selected = computed(() => props.run ?? runs.value[0]?.id ?? "");
const evidenceRun = computed(() => rating.value?.evidence?.regression_suite_run_id ?? null);
const goldenNotChecked = computed(() => {
  const golden = rating.value?.evidence?.golden_quotes;
  return golden?.status === "not_checked" ? golden.message : null;
});

function label(summary: RegressionRunSummary): string {
  const marked = summary.id === evidenceRun.value ? " · approval evidence" : "";
  return `${summary.finished_at} · ${summary.overall} · ${summary.id.slice(0, 8)}${marked}`;
}

async function load(): Promise<void> {
  loading.value = true;
  problem.value = null;
  result.value = null;
  try {
    rating.value = await getRatingVersionByRef(props.slug, Number(props.version));
    const listed = await listRegressionRuns(rating.value.id);
    runs.value = listed.items;
    truncated.value = listed.truncated;
    if (selected.value !== "") {
      result.value = await getRegressionRun(rating.value.id, selected.value);
    }
  } catch (error) {
    if (error instanceof ProblemError) problem.value = error;
    else throw error;
  } finally {
    loading.value = false;
  }
}

onMounted(load);
watch(() => props.run, load);

async function choose(event: Event): Promise<void> {
  const id = (event.target as HTMLSelectElement).value;
  await router.push({ query: id === "" ? {} : { run: id } });
}
</script>

<template>
  <section class="mx-auto max-w-5xl px-4 py-8">
    <p class="text-sm text-slate-500">
      <RouterLink
        v-if="rating"
        :to="`/rating-versions/${rating.id}`"
        class="hover:underline"
      >
        {{ heading }}
      </RouterLink>
      <span v-else>{{ heading }}</span>
      <span class="mx-1.5">/</span>
      Tests
    </p>
    <h1 class="mt-4 text-2xl font-semibold">
      Regression suite
      <span class="font-mono text-lg text-slate-500">{{ heading }}</span>
    </h1>

    <!-- Live regions are rendered persistently and only their content changes, so a screen
         reader announces the text (WCAG 4.1.3). -->
    <p
      role="status"
      class="mt-6 text-sm text-slate-500"
    >
      <template v-if="loading">
        Loading…
      </template>
      <template v-else-if="!problem && runs.length === 0">
        No regression runs.
      </template>
    </p>
    <div
      role="alert"
      :class="problem ? 'mt-6 rounded-md border border-red-200 bg-red-50 p-4' : ''"
    >
      <template v-if="problem">
        <p class="text-sm font-medium text-red-800">
          {{ problem.problem.title }}
        </p>
        <p class="mt-1 text-sm text-red-700">
          {{ problem.problem.detail }}
        </p>
      </template>
    </div>

    <template v-if="!loading && !problem && runs.length > 0">
      <div class="mt-4">
        <label
          for="regression-run"
          class="block text-sm font-medium"
        >Regression run</label>
        <select
          id="regression-run"
          :value="selected"
          class="mt-1 rounded-md border border-slate-300 px-2 py-1.5 font-mono text-sm"
          @change="choose"
        >
          <option
            v-for="summary in runs"
            :key="summary.id"
            :value="summary.id"
          >
            {{ label(summary) }}
          </option>
        </select>
        <p
          v-if="truncated"
          class="mt-1 text-sm text-slate-600"
        >
          Only the newest runs are listed.
        </p>
      </div>

      <template v-if="result">
        <p class="mt-4 text-sm">
          Overall: <strong>{{ result.overall }}</strong>
          <span class="ml-3 text-slate-500">suite {{ result.suite_ref }}</span>
        </p>

        <h2 class="mt-6 text-lg font-semibold">
          Golden quotes
        </h2>
        <table
          v-if="result.golden_results.length > 0"
          aria-label="Golden quotes"
          class="mt-2 w-full text-left text-sm"
        >
          <thead>
            <tr>
              <th scope="col">
                Quote
              </th>
              <th scope="col">
                Status
              </th>
              <th scope="col">
                Expected
              </th>
              <th scope="col">
                Actual
              </th>
              <th scope="col">
                Difference
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="golden in result.golden_results"
              :key="golden.name"
            >
              <td>{{ golden.name }}</td>
              <td>{{ golden.status }}</td>
              <td>{{ formatMinor(golden.expected_minor) }}</td>
              <td>{{ formatMinor(golden.actual_minor) }}</td>
              <td>{{ formatMinor(golden.difference_minor) }}</td>
            </tr>
          </tbody>
        </table>
        <p
          v-else
          class="mt-2 text-sm text-slate-600"
        >
          {{ goldenNotChecked ?? "This run holds no golden quotes." }}
        </p>

        <h2 class="mt-6 text-lg font-semibold">
          Properties
        </h2>
        <table
          aria-label="Property results"
          class="mt-2 w-full text-left text-sm"
        >
          <thead>
            <tr>
              <th scope="col">
                Property
              </th>
              <th scope="col">
                Status
              </th>
              <th scope="col">
                Cases
              </th>
              <th scope="col">
                Detail
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="property in result.property_results"
              :key="property.name"
            >
              <td>{{ property.name }}</td>
              <td>{{ property.status }}</td>
              <td>{{ property.cases_run }}</td>
              <td>
                <code v-if="property.error_code">{{ property.error_code }}</code>
                <!-- A MONOTONE_NO_COMPARABLE_PAIRS failure has no counterexample to show. -->
                <template
                  v-if="
                    property.status === 'fail' &&
                      property.counterexample &&
                      property.error_code !== 'MONOTONE_NO_COMPARABLE_PAIRS'
                  "
                >
                  <pre
                    :aria-label="`Counterexample of ${property.name}`"
                    class="mt-1 overflow-x-auto font-mono text-xs"
                  >{{ JSON.stringify(property.counterexample, null, 2) }}</pre>
                  <span
                    v-if="!property.counterexample_minimal"
                    class="text-xs text-amber-700"
                  >unminimised</span>
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </template>
    </template>
  </section>
</template>
