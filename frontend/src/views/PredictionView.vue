<script setup lang="ts">
import { computed, ref, watchEffect } from "vue";

import { getModel, listFactors, type Factor, type Model } from "@/api/models";
import { requiredColumns } from "@/api/predictionInputs";
import { predict, type Prediction, type PredictionInputRow } from "@/api/predictions";
import { ProblemError } from "@/api/problem";
import { getVersionById } from "@/api/versions";
import PredictionUncertainty from "@/components/PredictionUncertainty.vue";

const props = defineProps<{ slug: string; version?: string | undefined }>();

const model = ref<Model | null>(null);
const columns = ref<string[]>([]);
const unresolved = ref<string[]>([]);
const values = ref<Record<string, string>>({});
const prediction = ref<Prediction | null>(null);
const failure = ref<string | null>(null);
const loadFailure = ref<string | null>(null);
const scoring = ref(false);

/**
 * Resolve the columns one row must carry.
 *
 * Three reads, and a fourth only where the spec needs it.
 *
 * **The Dataset Version is resolved to its Dataset first, and that hop is not optional.** A
 * `Model` carries `dataset_version_id` and nothing else; `listFactors` filters by
 * `dataset_id`; and a Dataset Version is not a Dataset (`CLAUDE.md` §7). Passing the version
 * id straight to `listFactors` type-checks, because both are `string`, and returns the wrong
 * factor set at runtime. `FactorWorkbenchView.vue:130` does the same hop for the same reason,
 * and `getVersionById`'s own docstring names this case.
 *
 * `requiredColumns` is pure and handles one model, so an `offset.kind === "model"` spec is
 * completed here by resolving the referenced model and unioning its columns: the backend
 * computes that model's linear predictor on the frame *this* caller sends, so its factor
 * columns are caller-supplied too.
 */
watchEffect(async () => {
  loadFailure.value = null;
  try {
    const loaded = await getModel(props.slug, props.version ? Number(props.version) : undefined);
    model.value = loaded;
    const datasetVersion = await getVersionById(loaded.dataset_version_id);
    const factors = await listFactors(datasetVersion.dataset_id);
    const byId = new Map<string, Factor>(factors.map((factor) => [factor.id, factor]));
    const primary = requiredColumns(loaded, byId);
    const needed = new Set(primary.columns);
    const missing = [...primary.unresolvedFactorIds];

    if (primary.offsetModelRef !== null) {
      const source = await getModel(primary.offsetModelRef.slug, primary.offsetModelRef.version);
      const secondary = requiredColumns(source, byId);
      for (const column of secondary.columns) needed.add(column);
      missing.push(...secondary.unresolvedFactorIds);
    }

    columns.value = [...needed].sort();
    unresolved.value = missing;
    values.value = Object.fromEntries(columns.value.map((column) => [column, ""]));
  } catch (error) {
    loadFailure.value
      = error instanceof ProblemError
        ? (error.problem.detail ?? error.problem.title)
        : String(error);
  }
});

const row = computed<PredictionInputRow>(() =>
  Object.fromEntries(
    Object.entries(values.value).map(([column, raw]) => {
      if (raw === "") return [column, null];
      const asNumber = Number(raw);
      // A blank is a null, a numeric string is a number, and anything else stays a string:
      // the backend builds a frame from these and a categorical level is a string there too.
      return [column, raw.trim() !== "" && !Number.isNaN(asNumber) ? asNumber : raw];
    }),
  ),
);

/**
 * The refusals this page can receive, by code.
 *
 * Five of these share `409` and three distinct `VALIDATION_FAILED` messages share `422`, so
 * the branch is on `problem.code` — `problem.ts` states the rule on the field itself. The
 * server's `detail` is shown beneath, because it carries the specifics (which term, how many
 * rows) that a fixed sentence cannot.
 */
function refusalCopy(error: ProblemError): string {
  switch (error.code) {
    case "MODEL_NOT_FITTED":
      return "This model has not been fitted, so there is nothing to score with.";
    case "MODEL_INTERVAL_UNAVAILABLE":
      // FR-MODEL-78: crossing quantiles are detected and reported, never silently reordered.
      // This page therefore shows no interval at all here rather than an ordered one.
      return "The interval models cross on these rows, so no interval is reported for them.";
    case "MODEL_TYPE_UNSUPPORTED":
      return "This model's spec and fit result disagree about its type.";
    case "NOT_FOUND":
      return "No model with that name and version.";
    case "VALIDATION_FAILED":
      return "The request was refused — check the values below.";
    default:
      // `MODEL_TERM_UNRESOLVED` and its siblings arrive here. They are a 409 about the
      // pairing of a well-formed request with a real model: commonly a column the model was
      // fitted on that this row does not carry.
      return "These rows cannot be scored with this model.";
  }
}

async function score(): Promise<void> {
  if (model.value === null) return;
  scoring.value = true;
  failure.value = null;
  prediction.value = null;
  try {
    // 200, synchronously. No Job, no poll.
    prediction.value = await predict(model.value.id, row.value);
  } catch (error) {
    failure.value
      = error instanceof ProblemError
        ? `${refusalCopy(error)}${error.problem.detail ? ` ${error.problem.detail}` : ""}`
        : String(error);
  } finally {
    scoring.value = false;
  }
}

const first = computed(() => prediction.value?.rows[0] ?? null);
</script>

<template>
  <main class="mx-auto max-w-3xl p-6">
    <h1 class="text-xl font-semibold">
      Prediction
    </h1>
    <p
      v-if="model"
      class="text-sm text-slate-600"
    >
      {{ model.model_family_slug }}@{{ model.version }} &middot; {{ model.spec.model_type }}
    </p>

    <p
      v-if="loadFailure"
      role="alert"
      class="mt-4 rounded bg-amber-50 p-3 text-sm"
    >
      {{ loadFailure }}
    </p>

    <!-- A pinned factor that did not resolve means the form is missing a column, and a
         submission would fail with MODEL_TERM_UNRESOLVED. Said here rather than discovered
         at submit. -->
    <p
      v-if="unresolved.length"
      role="alert"
      class="mt-4 rounded bg-amber-50 p-3 text-sm"
    >
      {{ unresolved.length }} of this model's factors could not be resolved, so the form below
      is incomplete: {{ unresolved.join(", ") }}.
    </p>

    <form
      class="mt-6 grid gap-4 sm:grid-cols-2"
      @submit.prevent="score"
    >
      <div
        v-for="column in columns"
        :key="column"
      >
        <label
          :for="`field-${column}`"
          class="block text-xs font-medium text-slate-700"
        >
          {{ column }}
        </label>
        <input
          :id="`field-${column}`"
          v-model="values[column]"
          class="mt-1 w-full rounded border border-slate-300 px-2 py-1 text-sm"
          autocomplete="off"
        >
      </div>
      <div class="sm:col-span-2">
        <button
          type="submit"
          class="rounded bg-slate-900 px-4 py-2 text-sm text-white disabled:opacity-50"
          :disabled="scoring || model === null"
        >
          {{ scoring ? "Scoring…" : "Score row" }}
        </button>
      </div>
    </form>

    <p
      v-if="failure"
      role="alert"
      class="mt-4 rounded bg-amber-50 p-3 text-sm"
    >
      {{ failure }}
    </p>

    <PredictionUncertainty
      v-if="prediction && first"
      :uncertainty="prediction.uncertainty"
      :row="first"
    />

    <!-- `02` §5.1: production scoring is `03`'s batch path, not this route. -->
    <p class="mt-8 text-xs text-slate-500">
      Ad-hoc scoring, capped at development scale. A portfolio re-rate runs through the rating
      engine's batch scoring.
    </p>
  </main>
</template>
