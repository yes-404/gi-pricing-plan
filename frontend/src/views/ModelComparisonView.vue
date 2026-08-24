<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";

import type { ModelComparison } from "@/api/comparisons";
import { comparisonIdFromJob, getComparison, startComparison } from "@/api/comparisons";
import { TERMINAL, waitForJob } from "@/api/jobs";
import { ProblemError } from "@/api/problem";
import ComparisonMetricTable from "@/components/ComparisonMetricTable.vue";
import DoubleLiftChart from "@/components/DoubleLiftChart.vue";
import RelativityDiffTable from "@/components/RelativityDiffTable.vue";

/**
 * The poll budget, injectable so a test does not wait real seconds.
 *
 * Five minutes by default. No NFR names a budget for `MODEL_COMPARE`, so this is a chosen
 * ceiling rather than a measured one — which is safe only because running out of it renders
 * as "still running" and never as a failure.
 */
const props = withDefaults(defineProps<{ pollAttempts?: number; pollIntervalMs?: number }>(), {
  pollAttempts: 150,
  pollIntervalMs: 2000,
});

const route = useRoute();

const comparison = ref<ModelComparison | null>(null);
const problem = ref<ProblemError | null>(null);
/**
 * A discriminated stage rather than a set of booleans (RuleBuilder.vue's precedent). `waiting`
 * and `stalled` are different things to tell a user, which is why `waitForJob` returns a
 * non-terminal job rather than throwing.
 */
const stage = ref<"starting" | "waiting" | "ready" | "failed" | "stalled" | "refused">("starting");
const jobStage = ref("");
const failure = ref("");

/** `?ids=a,b` — UUIDs, because `CompareModels.model_ids` is a tuple of UUIDs. */
function idsFromQuery(): string[] {
  const raw = typeof route.query.ids === "string" ? route.query.ids : "";
  return raw
    .split(",")
    .map((id) => id.trim())
    .filter((id) => id.length > 0);
}

onMounted(async () => {
  const ids = idsFromQuery();
  // FR-MODEL-56 compares two or more; "one model measured against nothing is a diagnostics
  // read" (§4.11). Refusing here turns a 422 into a sentence.
  if (ids.length < 2) {
    stage.value = "refused";
    failure.value =
      "Select two or more models to compare — one model measured against nothing is a diagnostics read.";
    return;
  }

  try {
    const accepted = await startComparison(ids);
    stage.value = "waiting";
    const job = await waitForJob(accepted.id, {
      attempts: props.pollAttempts,
      intervalMs: props.pollIntervalMs,
      onPoll: (polled) => {
        jobStage.value = polled.progress?.stage ?? "";
      },
    });

    // `waitForJob` returns whatever state it reached, so all three outcomes arrive here.
    if (!TERMINAL.includes(job.status)) {
      stage.value = "stalled";
      return;
    }
    if (job.status !== "succeeded") {
      stage.value = "failed";
      failure.value = job.error?.message ?? `The comparison ${job.status}.`;
      return;
    }

    const comparisonId = comparisonIdFromJob(job);
    if (comparisonId === null) {
      stage.value = "failed";
      failure.value = "The comparison finished but did not name an artifact to read.";
      return;
    }
    comparison.value = await getComparison(comparisonId);
    stage.value = "ready";
  } catch (error) {
    // A ProblemError from the POST is a complete answer — every comparability rule is
    // decided before a Job exists, so a 409 here means the request was wrong, not that a run
    // failed. Anything that is not a problem document is rethrown, never swallowed.
    if (error instanceof ProblemError) {
      problem.value = error;
      stage.value = "failed";
    } else throw error;
  }
});
</script>

<template>
  <section>
    <header class="mb-5">
      <RouterLink
        to="/models"
        class="text-sm text-slate-500 underline"
      >
        Models
      </RouterLink>
      <h1 class="mt-1 text-xl font-semibold tracking-tight">
        Model comparison
      </h1>
      <p
        v-if="comparison"
        class="mt-1 text-sm text-slate-500"
      >
        {{ comparison.summary.model_refs.length }} models on a shared holdout of
        {{ comparison.summary.holdout_rows }} rows
        <span class="font-mono text-xs">({{ comparison.summary.split_ref.holdout_part }})</span>
      </p>
    </header>

    <p
      v-if="stage === 'starting' || stage === 'waiting'"
      role="status"
      class="text-sm text-slate-500"
    >
      {{ stage === "starting" ? "Starting the comparison…" : `Scoring the holdout…${jobStage ? ` ${jobStage}` : ""}` }}
    </p>

    <p
      v-else-if="stage === 'stalled'"
      role="status"
      class="rounded-md border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900"
    >
      The comparison is still running. It has not failed — reload this page to pick it up.
    </p>

    <div
      v-else-if="stage === 'failed' || stage === 'refused'"
      role="alert"
      class="rounded-md border border-red-200 bg-red-50 p-4"
    >
      <p class="font-medium text-red-900">
        {{ problem ? problem.problem.title : "The comparison did not produce a result" }}
      </p>
      <p class="mt-1 text-sm text-red-800">
        {{ problem ? problem.problem.detail : failure }}
      </p>
    </div>

    <template v-else-if="comparison">
      <h2 class="mt-6 text-sm font-semibold uppercase tracking-wide text-slate-500">
        Aligned metrics
      </h2>
      <ComparisonMetricTable
        :metrics="comparison.summary.metrics"
        :model-refs="comparison.summary.model_refs"
      />

      <template v-if="comparison.summary.double_lift.length">
        <h2 class="mt-8 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Double lift
        </h2>
        <div
          v-for="series in comparison.summary.double_lift"
          :key="series.challenger_ref"
        >
          <p class="mt-3 text-sm text-slate-500">
            Baseline against {{ series.challenger_ref }}, {{ series.weighting }}-weighted, binned by
            the ratio of the two predictions
          </p>
          <DoubleLiftChart :series="series" />
        </div>
      </template>

      <template v-if="comparison.summary.relativity_differences.length">
        <h2 class="mt-8 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Relativity differences
        </h2>
        <RelativityDiffTable
          :differences="comparison.summary.relativity_differences"
          :model-refs="comparison.summary.model_refs"
        />
      </template>
    </template>
  </section>
</template>
