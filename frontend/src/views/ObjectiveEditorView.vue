<script setup lang="ts">
/**
 * `02` §5.3's Custom objective editor, `/objectives/new` (WK-690 Slice 5, FR-1840, RL-1616).
 *
 * **One parser, and it is not here.** Parse errors, the derived gradient and hessian, and the
 * loss-curve points all come from the stateless preview route (`previewObjective`); nothing in
 * this file parses, differentiates or evaluates the loss. The preview is debounced, so a burst
 * of keystrokes is one call (RL-1616 refuses a draft, or a call, per keystroke).
 *
 * **Create-only** (RL-1616, need 5.8): saving creates a `draft` — `POST /custom-objectives`
 * versions on a reused slug — and there is no edit control. Derive, certify and submit follow
 * on the objective's certificate page.
 *
 * **The flag is read from the route's own answer.** The frontend has no settings read, so a
 * 409 `OBJECTIVE_KIND_NOT_ENABLED` from the first preview is what disables the editor.
 */
import { computed, nextTick, onBeforeUnmount, reactive, ref, watch } from "vue";

import {
  createObjective,
  previewObjective,
  type CreateCustomObjective,
  type CustomObjective,
  type ObjectivePreview,
  type ObjectivePreviewRequest,
} from "@/api/objectives";
import { ProblemError } from "@/api/problem";
import ObjectiveLossCurve from "@/components/ObjectiveLossCurve.vue";

type Applicability = NonNullable<CreateCustomObjective["applicability"]>;
type Response = Applicability["responses"][number];

/** Debounce for the live preview, in milliseconds. */
const PREVIEW_DELAY_MS = 600;

/** The response kinds an objective can be offered for (`ResponseKind`; `satisfies` catches a removal). */
const RESPONSES = [
  "claim_count", "claim_severity", "burning_cost", "conversion", "retention",
] as const satisfies readonly Response[];
// The editor targets the boosters, the two backends that run a custom objective, and a
// non-negative response — the §4.6 example's domain. Applicability is required for an
// `expression` objective (RL-1410 R3), and an author may narrow but never widen it.
const BACKENDS: Applicability["backends"] = ["xgboost", "lightgbm"];
const SYMBOLS: NonNullable<CreateCustomObjective["bound_symbols"]> = ["y", "f", "w"];
const GRID_POINTS = 100;

interface ParameterRow {
  name: string;
  default: number;
  min: number;
  max: number;
  /** The value the curve is drawn at. */
  value: number;
}

const slug = ref("");
const loss = ref("");
const parameters = reactive<ParameterRow[]>([]);
const responses = ref<Response[]>(["burning_cost", "claim_severity"]);
const grid = reactive({ y: 100, w: 1, from: 3, to: 6 });

const preview = ref<ObjectivePreview | null>(null);
const refusal = ref<string | null>(null);
const notEnabled = ref(false);
const created = ref<CustomObjective | null>(null);
const createFailure = ref<string | null>(null);
const statusEl = ref<HTMLElement | null>(null);

const declared = computed(() => parameters.filter((row) => row.name !== ""));

function previewRequest(): ObjectivePreviewRequest {
  return {
    loss: loss.value,
    parameters: declared.value.map(({ name, default: value, min, max }) => ({
      name, type: "float", default: value, min, max,
    })),
    values: Object.fromEntries(declared.value.map((row) => [row.name, row.value])),
    grid: { y: grid.y, w: grid.w, f_range: [grid.from, grid.to], n_points: GRID_POINTS },
  };
}

let timer: ReturnType<typeof setTimeout> | undefined;
let latest = 0;

async function runPreview() {
  const call = ++latest;
  try {
    const answer = await previewObjective(previewRequest());
    if (call !== latest) return;
    preview.value = answer;
    refusal.value = null;
  } catch (error) {
    if (call !== latest) return;
    preview.value = null;
    if (error instanceof ProblemError && error.code === "OBJECTIVE_KIND_NOT_ENABLED") {
      notEnabled.value = true;
      refusal.value = null;
      // The textarea the user was typing in is now disabled, which would drop focus to the body.
      void nextTick(() => statusEl.value?.focus());
    } else {
      refusal.value = error instanceof Error ? error.message : String(error);
    }
  }
}

watch(
  [loss, grid, () => parameters.map((row) => ({ ...row }))],
  () => {
    clearTimeout(timer);
    if (loss.value.trim() === "") {
      latest++;
      preview.value = null;
      refusal.value = null;
      return;
    }
    timer = setTimeout(() => void runPreview(), PREVIEW_DELAY_MS);
  },
  { deep: true },
);
onBeforeUnmount(() => clearTimeout(timer));

const grammarError = computed(() => {
  const error = preview.value?.error;
  if (error?.reason !== "grammar") return null;
  const where = error.line == null ? "" : `line ${error.line}, column ${error.column ?? "?"}: `;
  return `${where}${error.message}`;
});
const timedOut = computed(() => preview.value?.error?.reason === "timeout");

const canCreate = computed(
  () => !notEnabled.value && slug.value !== "" && loss.value !== "" && responses.value.length > 0,
);

function addParameter() {
  parameters.push({ name: "", default: 1, min: 0, max: 10, value: 1 });
  void nextTick(() => {
    const names = document.querySelectorAll<HTMLInputElement>("[data-parameter-name]");
    names[names.length - 1]?.focus();
  });
}

function create() {
  createFailure.value = null;
  const body: CreateCustomObjective = {
    slug: slug.value,
    kind: "expression",
    bound_symbols: SYMBOLS,
    parameters: declared.value.map(({ name, default: value, min, max }) => ({
      name, type: "float", default: value, min, max,
    })),
    loss: loss.value,
    applicability: {
      responses: responses.value,
      backends: BACKENDS,
      offset_required: false,
      y_domain: { min_inclusive: 0 },
    },
  };
  createObjective(body).then(
    (objective) => {
      created.value = objective;
    },
    (error: unknown) => {
      createFailure.value = error instanceof Error ? error.message : String(error);
    },
  );
}
</script>

<template>
  <section class="max-w-4xl p-6">
    <h1 class="mb-4 text-xl font-semibold">
      New expression objective
    </h1>

    <div
      ref="statusEl"
      role="status"
      tabindex="-1"
      class="mb-4 text-sm"
    >
      <p
        v-if="notEnabled"
        class="rounded border border-slate-500 bg-slate-50 p-3"
      >
        Expression objectives are not enabled in this workspace
        (<code>features.expression_objectives_enabled</code> is off).
      </p>
      <p v-else-if="timedOut">
        The preview timed out. The loss may still be valid; try a simpler expression.
      </p>
      <p v-else-if="created">
        Created {{ created.slug }} version {{ created.version }} as a draft.
        <a
          :href="`/objectives/${created.id}/certificate`"
          class="text-blue-700 underline"
        >Open it to derive, certify and submit</a>.
      </p>
    </div>

    <div class="space-y-4">
      <div>
        <label
          for="objective-slug"
          class="block text-sm font-medium"
        >Slug (required)</label>
        <input
          id="objective-slug"
          v-model="slug"
          type="text"
          required
          :disabled="notEnabled"
          class="mt-1 w-full rounded border border-slate-500 px-2 py-1 text-sm"
        >
      </div>

      <div>
        <label
          for="objective-loss"
          class="block text-sm font-medium"
        >Loss L(y, f, w) (required)</label>
        <textarea
          id="objective-loss"
          v-model="loss"
          rows="3"
          spellcheck="false"
          required
          :aria-invalid="grammarError !== null"
          aria-describedby="objective-loss-error"
          :disabled="notEnabled"
          class="mt-1 w-full rounded border border-slate-500 px-2 py-1 font-mono text-sm"
        />
        <p
          v-if="grammarError"
          id="objective-loss-error"
          role="alert"
          class="mt-1 text-sm text-red-700"
        >
          {{ grammarError }}
        </p>
        <p
          v-else-if="refusal"
          role="alert"
          class="mt-1 text-sm text-red-700"
        >
          {{ refusal }}
        </p>
      </div>

      <fieldset>
        <legend class="text-sm font-medium">
          Parameters
        </legend>
        <div
          v-for="(row, index) in parameters"
          :key="index"
          role="group"
          :aria-label="`Parameter ${index + 1}`"
          class="mt-2 flex flex-wrap items-end gap-2 text-sm"
        >
          <label>Name
            <input
              v-model="row.name"
              type="text"
              :aria-label="`Parameter ${index + 1} name`"
              data-parameter-name
              :disabled="notEnabled"
              class="block w-28 rounded border border-slate-500 px-2 py-1"
            ></label>
          <label>Default
            <input
              v-model.number="row.default"
              type="number"
              :disabled="notEnabled"
              class="block w-20 rounded border border-slate-500 px-2 py-1"
            ></label>
          <label>Min
            <input
              v-model.number="row.min"
              type="number"
              :disabled="notEnabled"
              class="block w-20 rounded border border-slate-500 px-2 py-1"
            ></label>
          <label>Max
            <input
              v-model.number="row.max"
              type="number"
              :disabled="notEnabled"
              class="block w-20 rounded border border-slate-500 px-2 py-1"
            ></label>
          <label>Preview at
            <input
              v-model.number="row.value"
              type="number"
              :disabled="notEnabled"
              class="block w-20 rounded border border-slate-500 px-2 py-1"
            ></label>
          <button
            type="button"
            :aria-label="`Remove parameter ${index + 1}`"
            class="rounded border border-slate-500 px-2 py-1"
            @click="parameters.splice(index, 1)"
          >
            Remove
          </button>
        </div>
        <button
          type="button"
          :disabled="notEnabled"
          class="mt-2 rounded border border-slate-500 px-2 py-1 text-sm"
          @click="addParameter"
        >
          Add parameter
        </button>
      </fieldset>

      <fieldset class="flex flex-wrap gap-3 text-sm">
        <legend class="text-sm font-medium">
          Curve at one observation
        </legend>
        <label>y
          <input
            v-model.number="grid.y"
            type="number"
            :disabled="notEnabled"
            class="block w-24 rounded border border-slate-500 px-2 py-1"
          ></label>
        <label>Weight w
          <input
            v-model.number="grid.w"
            type="number"
            :disabled="notEnabled"
            class="block w-24 rounded border border-slate-500 px-2 py-1"
          ></label>
        <label>Score f from
          <input
            v-model.number="grid.from"
            type="number"
            :disabled="notEnabled"
            class="block w-24 rounded border border-slate-500 px-2 py-1"
          ></label>
        <label>Score f to
          <input
            v-model.number="grid.to"
            type="number"
            :disabled="notEnabled"
            class="block w-24 rounded border border-slate-500 px-2 py-1"
          ></label>
      </fieldset>

      <fieldset class="text-sm">
        <legend class="text-sm font-medium">
          Applicable responses
        </legend>
        <label
          v-for="kind in RESPONSES"
          :key="kind"
          class="mr-4 inline-flex items-center gap-1"
        >
          <input
            v-model="responses"
            type="checkbox"
            :value="kind"
            :disabled="notEnabled"
          >{{ kind }}</label>
      </fieldset>
    </div>

    <div
      v-if="preview?.gradient != null"
      class="mt-6 space-y-2 text-sm"
    >
      <h2 class="font-semibold">
        Derived by the platform
      </h2>
      <p class="break-words">
        Gradient: <code class="break-words font-mono">{{ preview.gradient }}</code>
      </p>
      <p class="break-words">
        Hessian: <code class="break-words font-mono">{{ preview.hessian }}</code>
      </p>
    </div>

    <ObjectiveLossCurve
      v-if="preview?.curve"
      :curve="preview.curve"
    />

    <div class="mt-6">
      <button
        type="button"
        :disabled="!canCreate"
        class="rounded bg-slate-800 px-3 py-1.5 text-sm text-white disabled:opacity-50"
        @click="create"
      >
        Create objective
      </button>
      <p
        v-if="!canCreate && !notEnabled"
        class="mt-1 text-xs text-slate-700"
      >
        Needs a slug, a loss and at least one applicable response.
      </p>
      <p
        v-if="createFailure"
        role="alert"
        class="mt-2 text-sm text-red-700"
      >
        {{ createFailure }}
      </p>
    </div>
  </section>
</template>
