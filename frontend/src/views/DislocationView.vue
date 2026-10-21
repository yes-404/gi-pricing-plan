<script setup lang="ts">
/**
 * The dislocation views' route (03 §5.3): `/rating/:slug/v/:version/dislocation`. `:slug` and
 * `:version` are the Rating Version's own (RL-1473). The run is cited by id in `?run=` (FR-265:
 * a persisted artifact, not a transient screen), so a link to this page names the run it
 * shows. The histogram, segment grid and attribution waterfall read the run alone; the movers
 * table reads `/movers` through the generated `DislocationMover`.
 */
import { computed, onMounted, ref, watch } from "vue";
import { RouterLink, useRouter } from "vue-router";

import {
  getDislocationMovers,
  getDislocationRun,
  type DislocationMover,
  type DislocationRun,
} from "@/api/dislocationRuns";
import { ProblemError } from "@/api/problem";
import { getRatingVersionByRef, type RatingVersion } from "@/api/ratingVersions";
import AttributionWaterfall from "@/components/dislocation/AttributionWaterfall.vue";
import ChangeHistogram from "@/components/dislocation/ChangeHistogram.vue";
import { formatMinor, formatPct } from "@/components/dislocation/format";
import LargestMovers from "@/components/dislocation/LargestMovers.vue";
import SegmentGrid from "@/components/dislocation/SegmentGrid.vue";

const props = defineProps<{ slug: string; version: string; run?: string }>();
const router = useRouter();

const rating = ref<RatingVersion | null>(null);
const result = ref<DislocationRun | null>(null);
const movers = ref<DislocationMover[]>([]);
const loading = ref(true);
const problem = ref<ProblemError | null>(null);
const moversProblem = ref<ProblemError | null>(null);
const runId = ref(props.run ?? "");

const heading = computed(() => `${props.slug}@${props.version}`);

async function load(): Promise<void> {
  result.value = null;
  movers.value = [];
  problem.value = null;
  moversProblem.value = null;
  if (!props.run) {
    loading.value = false;
    return;
  }
  loading.value = true;
  try {
    result.value = await getDislocationRun(props.run);
    try {
      movers.value = await getDislocationMovers(props.run);
    } catch (error) {
      // The movers need `dataset:read` as well; the rest of the run is still shown.
      if (error instanceof ProblemError) moversProblem.value = error;
      else throw error;
    }
  } catch (error) {
    if (error instanceof ProblemError) problem.value = error;
    else throw error;
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  try {
    rating.value = await getRatingVersionByRef(props.slug, Number(props.version));
  } catch (error) {
    if (!(error instanceof ProblemError)) throw error;
  }
  await load();
});
watch(() => props.run, load);

async function cite(): Promise<void> {
  const id = runId.value.trim();
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
      Dislocation
    </p>
    <h1 class="mt-4 text-2xl font-semibold">
      Dislocation
      <span class="font-mono text-lg text-slate-500">{{ heading }}</span>
    </h1>

    <form
      class="mt-4 flex items-end gap-2"
      @submit.prevent="cite"
    >
      <div>
        <label
          for="dislocation-run-id"
          class="block text-sm font-medium"
        >Dislocation Run id</label>
        <input
          id="dislocation-run-id"
          v-model="runId"
          type="text"
          class="mt-1 w-96 rounded-md border border-slate-300 px-2 py-1.5 font-mono text-sm"
        >
      </div>
      <button
        type="submit"
        class="rounded-md border border-slate-300 px-3 py-1.5 text-sm"
      >
        Show run
      </button>
    </form>

    <p
      v-if="loading"
      role="status"
      class="mt-6 text-sm text-slate-500"
    >
      Loading…
    </p>
    <div
      v-else-if="problem"
      role="alert"
      class="mt-6 rounded-md border border-red-200 bg-red-50 p-4"
    >
      <p class="text-sm font-medium text-red-800">
        {{ problem.problem.title }}
      </p>
      <p class="mt-1 text-sm text-red-700">
        {{ problem.problem.detail }}
      </p>
    </div>
    <p
      v-else-if="!result"
      class="mt-6 text-sm text-slate-500"
    >
      Cite a Dislocation Run by its id to see it.
    </p>

    <template v-else>
      <dl class="mt-6 grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-sm">
        <dt class="text-slate-500">
          Baseline
        </dt>
        <dd class="font-mono">
          {{ result.baseline_ref }}
        </dd>
        <dt class="text-slate-500">
          Candidate
        </dt>
        <dd class="font-mono">
          {{ result.candidate_ref }}
        </dd>
        <dt class="text-slate-500">
          Policies
        </dt>
        <dd>{{ result.policy_count }}</dd>
        <dt class="text-slate-500">
          Baseline premium
        </dt>
        <dd>{{ formatMinor(result.totals.baseline_premium_minor) }}</dd>
        <dt class="text-slate-500">
          Candidate premium
        </dt>
        <dd>{{ formatMinor(result.totals.candidate_premium_minor) }}</dd>
        <dt class="text-slate-500">
          Total change
        </dt>
        <dd>{{ formatPct(result.totals.change_pct) }}</dd>
      </dl>

      <ChangeHistogram :bands="result.distribution" />
      <SegmentGrid
        :segments="result.by_segment ?? []"
        :rungs="result.by_ladder_rung ?? []"
      />
      <AttributionWaterfall
        :items="result.attribution"
        :summary="result.attribution_summary"
      />
      <p
        v-if="moversProblem"
        role="status"
        class="mt-6 text-sm text-slate-600"
      >
        The largest movers could not be loaded: {{ moversProblem.problem.detail }}
      </p>
      <LargestMovers
        v-else
        :movers="movers"
      />
    </template>
  </section>
</template>
