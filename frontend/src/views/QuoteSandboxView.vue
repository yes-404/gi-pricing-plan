<script setup lang="ts">
/**
 * The quote sandbox's route (03 §5.3): `/rating/:slug/v/:version/sandbox`. `:slug` and
 * `:version` are the Rating Version's own (RL-1473). It builds a quote form from the input
 * contract of the algorithm that version pins, scores the version in view through an explicit
 * `rating_version_ref` (FR-251, `purpose: what_if`), and shows the outcome, the ladder
 * waterfall and the trace. The trace is requested on every score (FR-258), so the waterfall
 * is on the same page as the quote it explains (FR-25). No scoring rule lives here.
 */
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";

import { getRatingAlgorithm, type RatingAlgorithm } from "@/api/ratingAlgorithms";
import { getRatingVersionByRef, type RatingVersion } from "@/api/ratingVersions";
import { ProblemError } from "@/api/problem";
import { scoreQuote, type ScoringResult } from "@/api/score";
import { parseRef } from "@/components/dag/graph";
import LadderWaterfall from "@/components/sandbox/LadderWaterfall.vue";
import QuoteError from "@/components/sandbox/QuoteError.vue";
import QuoteForm from "@/components/sandbox/QuoteForm.vue";
import QuoteOutcome from "@/components/sandbox/QuoteOutcome.vue";
import type { QuoteFormSubmit } from "@/components/sandbox/quoteForm";
import TraceTimeline from "@/components/sandbox/TraceTimeline.vue";

const props = defineProps<{ slug: string; version: string }>();

/** The API carries no workspace currency yet (OQ-551); money is shown in sterling. */
const CURRENCY = "GBP";

const rating = ref<RatingVersion | null>(null);
const algorithm = ref<RatingAlgorithm | null>(null);
const loading = ref(true);
const loadProblem = ref<ProblemError | null>(null);
const pinsNoAlgorithm = ref(false);

const scoring = ref(false);
const result = ref<ScoringResult | null>(null);
const scoreProblem = ref<ProblemError | null>(null);

const versionRef = computed(() => `rating_version:${props.slug}@${props.version}`);

onMounted(async () => {
  try {
    const found = await getRatingVersionByRef(props.slug, Number(props.version));
    rating.value = found;
    if (found.algorithm_ref) {
      const ref_ = parseRef(found.algorithm_ref);
      algorithm.value = await getRatingAlgorithm(ref_.slug, ref_.version);
    } else {
      pinsNoAlgorithm.value = true;
    }
  } catch (error) {
    if (error instanceof ProblemError) loadProblem.value = error;
    else throw error;
  } finally {
    loading.value = false;
  }
});

async function score(form: QuoteFormSubmit): Promise<void> {
  scoring.value = true;
  scoreProblem.value = null;
  result.value = null;
  try {
    result.value = await scoreQuote({
      purpose: form.purpose,
      quoted_at: new Date().toISOString(),
      effective_date: form.effective_date,
      inputs: form.inputs,
      options: { rating_version_ref: versionRef.value, trace: true },
    });
  } catch (error) {
    if (error instanceof ProblemError) scoreProblem.value = error;
    else throw error;
  } finally {
    scoring.value = false;
  }
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
        {{ rating.slug }}@{{ rating.version }}
      </RouterLink>
      <span class="mx-1.5">/</span>
      Quote sandbox
    </p>

    <p
      v-if="loading"
      role="status"
      class="mt-6 text-sm text-slate-500"
    >
      Loading…
    </p>

    <div
      v-else-if="loadProblem"
      role="alert"
      class="mt-6 rounded-md border border-red-200 bg-red-50 p-4"
    >
      <p class="text-sm font-medium text-red-800">
        {{ loadProblem.problem.title }}
      </p>
      <p class="mt-1 text-sm text-red-700">
        {{ loadProblem.problem.detail }}
      </p>
    </div>

    <template v-else-if="rating">
      <h1 class="mt-4 text-2xl font-semibold">
        Quote sandbox
        <span class="font-mono text-lg text-slate-500">{{ rating.slug }}@{{ rating.version }}</span>
      </h1>

      <p
        v-if="pinsNoAlgorithm || !algorithm"
        role="status"
        class="mt-4 text-sm text-slate-600"
      >
        This Rating Version pins no algorithm, so there is no input contract to build a quote
        from.
      </p>

      <div
        v-else
        class="mt-6 grid gap-8 lg:grid-cols-[22rem_1fr]"
      >
        <QuoteForm
          :fields="algorithm.input_contract"
          :submitting="scoring"
          @submit="score"
        />

        <div class="space-y-8">
          <QuoteError
            v-if="scoreProblem"
            :error="scoreProblem"
          />
          <template v-if="result">
            <QuoteOutcome :result="result" />
            <LadderWaterfall
              :rungs="result.premium_ladder"
              :currency="CURRENCY"
            />
            <TraceTimeline
              v-if="result.trace"
              :trace="result.trace"
            />
          </template>
          <p
            v-else-if="!scoreProblem"
            class="text-sm text-slate-500"
          >
            Score a quote to see its outcome, ladder and trace.
          </p>
        </div>
      </div>
    </template>
  </section>
</template>
