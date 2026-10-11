<script setup lang="ts">
/**
 * The DAG designer's route (03 §5.3): `/rating/:slug/v/:version/design`. `:slug` and
 * `:version` are the Rating Version's own (RL-1473); it loads the algorithm that version pins
 * and saves an edit as a new algorithm version, never in place (RL-1475). No graph rule lives
 * here: a refused save shows the server's own code and detail (RL-1474).
 */
import { computed, defineAsyncComponent, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";

import {
  getRatingAlgorithm,
  saveRatingAlgorithm,
  type RatingAlgorithmDraft,
} from "@/api/ratingAlgorithms";
import { ProblemError } from "@/api/problem";
import { getRatingVersionByRef, type RatingVersion } from "@/api/ratingVersions";
import { parseRef } from "@/components/dag/graph";
import { stepProblems } from "@/components/dag/problems";

// Async, so `@vue-flow` stays in its own lazy chunk even if another view imports this one.
const DagDesigner = defineAsyncComponent(() => import("@/components/dag/DagDesigner.vue"));

const props = defineProps<{ slug: string; version: string }>();

const rating = ref<RatingVersion | null>(null);
const draft = ref<RatingAlgorithmDraft | null>(null);
const pinsNoAlgorithm = ref(false);
const nextVersion = ref(1);
const loading = ref(true);
const loadProblem = ref<ProblemError | null>(null);
const saveProblem = ref<ProblemError | null>(null);
const saved = ref<string | null>(null);
const saving = ref(false);
let idempotencyKey = crypto.randomUUID();

onMounted(async () => {
  try {
    const version = await getRatingVersionByRef(props.slug, Number(props.version));
    rating.value = version;
    if (version.algorithm_ref) {
      const ref_ = parseRef(version.algorithm_ref);
      const algorithm = await getRatingAlgorithm(ref_.slug, ref_.version);
      draft.value = algorithm;
      nextVersion.value = algorithm.version + 1;
    } else {
      pinsNoAlgorithm.value = true;
      draft.value = {
        slug: version.slug,
        version: 1,
        input_contract: [],
        outputs: [],
        steps: [],
        sub_graphs: [],
      };
      nextVersion.value = 1;
    }
  } catch (error) {
    if (error instanceof ProblemError) loadProblem.value = error;
    else throw error;
  } finally {
    loading.value = false;
  }
});

const problems = computed(() =>
  (draft.value?.steps ?? []).flatMap((step) =>
    stepProblems(step).map((problem) => `${step.step_id}: ${problem}`),
  ),
);
const versionValid = computed(() => Number.isInteger(nextVersion.value) && nextVersion.value >= 1);
const canSave = computed(
  () => draft.value !== null && problems.value.length === 0 && versionValid.value && !saving.value,
);

async function save(): Promise<void> {
  if (draft.value === null || !canSave.value) return;
  saving.value = true;
  saved.value = null;
  saveProblem.value = null;
  try {
    const result = await saveRatingAlgorithm(
      { ...draft.value, version: nextVersion.value },
      idempotencyKey,
    );
    saved.value = `Saved as ${result.slug}@${result.version}`;
  } catch (error) {
    if (error instanceof ProblemError) saveProblem.value = error;
    else throw error;
  } finally {
    idempotencyKey = crypto.randomUUID();
    saving.value = false;
  }
}
</script>

<template>
  <section class="mx-auto max-w-7xl px-4 py-8">
    <p class="text-sm text-slate-500">
      <RouterLink
        v-if="rating"
        :to="`/rating-versions/${rating.id}`"
        class="hover:underline"
      >
        {{ rating.slug }}@{{ rating.version }}
      </RouterLink>
      <span class="mx-1.5">/</span>
      Designer
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

    <template v-else-if="rating && draft">
      <h1 class="mt-4 text-2xl font-semibold">
        Design {{ draft.slug }}
        <span class="font-mono text-lg text-slate-500">for {{ rating.slug }}@{{ rating.version }}</span>
      </h1>

      <p
        v-if="pinsNoAlgorithm"
        role="status"
        class="mt-4 rounded-md border border-sky-200 bg-sky-50 p-3 text-sm text-sky-900"
      >
        This Rating Version pins no algorithm yet. Saving creates {{ rating.slug }}@1; pinning it to the version is not part of this view.
      </p>

      <div class="mt-4 flex flex-wrap items-end gap-3">
        <div>
          <label
            for="rd-version"
            class="mb-1 block text-sm font-medium text-slate-700"
          >Algorithm version</label>
          <input
            id="rd-version"
            v-model.number="nextVersion"
            type="number"
            min="1"
            step="1"
            class="w-28 rounded-md border border-slate-300 px-2 py-1 text-sm"
          >
        </div>
        <button
          type="button"
          class="rounded-md bg-sky-700 px-4 py-1.5 text-sm font-medium text-white aria-disabled:opacity-50"
          :aria-disabled="!canSave"
          :aria-describedby="problems.length > 0 ? 'rd-problems' : undefined"
          @click="save"
        >
          Save as new version
        </button>
      </div>

      <ul
        v-if="problems.length > 0"
        id="rd-problems"
        aria-label="Fields to fill before saving"
        class="mt-3 list-disc pl-5 text-sm text-red-700"
      >
        <li
          v-for="problem in problems"
          :key="problem"
        >
          {{ problem }}
        </li>
      </ul>
      <p
        role="status"
        class="mt-3 text-sm text-green-800"
      >
        {{ saved }}
      </p>
      <div
        v-if="saveProblem"
        role="alert"
        class="mt-3 rounded-md border border-red-200 bg-red-50 p-3"
      >
        <p class="text-sm font-medium text-red-800">
          {{ saveProblem.code }}: {{ saveProblem.problem.title }}
        </p>
        <p class="mt-1 text-sm text-red-700">
          {{ saveProblem.problem.detail }}
        </p>
      </div>

      <div class="mt-6">
        <DagDesigner
          v-model:draft="draft"
          :version-mode="rating.model_reference_mode"
          :rate-table-pins="(rating.pins?.rate_tables ?? []).map(String)"
        />
      </div>
    </template>
  </section>
</template>
