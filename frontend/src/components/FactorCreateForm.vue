<script setup lang="ts">
/**
 * Create a Factor from a profiled column, with `02` §5.3's intent and monotonic-direction
 * controls.
 *
 * **Creation only, and there is no edit.** A Factor's intent is immutable: `Factor` is
 * `frozen=True`, `/factors` carries GET and POST alone with no `PATCH` or `PUT`, and a POST
 * with an existing slug allocates version N+1 rather than mutating (FR-MODEL-7). So this
 * form sets intent once. There is deliberately **no "re-version to change intent"
 * affordance** — re-versioning changes what every future Model Spec naming that slug fits
 * on, which is a separate capability and not this slice's to invent.
 *
 * **Only two of the contract's four intents are offered.** `offset` and `diagnostic` are
 * superseded (FR-MODEL-116, FR-MODEL-120) and keep their arm in the published contract
 * deliberately, so the union will never narrow. The refused pair is pinned against
 * `pricing-core`'s own `REFUSED_FACTOR_INTENTS` rather than against prose — see
 * `@/api/models`. This is the guard, not a convenience: `POST /factors` accepts all four,
 * so an unoffered intent would be accepted, stored and audited, then fail at fit.
 *
 * **A direction requires a rationale**, because `Factor`'s own validator requires it
 * (FR-MODEL-4: "the direction is an actuarial judgement, and the next person needs to know
 * whose and why"). Enforced here so the answer is a disabled button rather than a 422.
 */
import { computed, ref } from "vue";

import {
  createFactor,
  FACTOR_INTENT_LABELS,
  MONOTONIC_DIRECTION_LABELS,
  OFFERED_FACTOR_INTENTS,
  type Factor,
  type FactorIntent,
  type MonotonicDirection,
} from "@/api/models";
import { ProblemError } from "@/api/problem";
import FormField from "@/components/FormField.vue";

const props = defineProps<{ datasetId: string; columns: readonly string[] }>();
const emit = defineEmits<{ created: [Factor] }>();

const column = ref("");
const slug = ref("");
const intent = ref<FactorIntent>("risk");
const direction = ref<MonotonicDirection>("none");
const rationale = ref("");
const busy = ref(false);
const problem = ref<ProblemError | null>(null);
const created = ref<Factor | null>(null);

/** FR-MODEL-4's rule, enforced before the request rather than discovered in its refusal. */
const rationaleRequired = computed(() => direction.value !== "none");
const ready = computed(
  () =>
    Boolean(column.value)
    && Boolean(slug.value.trim())
    && (!rationaleRequired.value || Boolean(rationale.value.trim())),
);

async function submit(): Promise<void> {
  if (!ready.value) return;
  busy.value = true;
  problem.value = null;
  created.value = null;
  try {
    const factor = await createFactor({
      slug: slug.value.trim(),
      dataset_id: props.datasetId,
      source_columns: [column.value],
      intent: intent.value,
      monotonic_direction: direction.value,
      // Omitted rather than sent empty when there is no direction: the field is
      // `str | None`, and "" is a rationale that says nothing.
      ...(rationaleRequired.value ? { monotonic_rationale: rationale.value.trim() } : {}),
    });
    created.value = factor;
    emit("created", factor);
  } catch (caught) {
    if (!(caught instanceof ProblemError)) throw caught;
    problem.value = caught;
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <section class="rounded-md border border-slate-200 p-4">
    <h2 class="mb-3 text-sm font-medium text-slate-700">
      New factor
    </h2>

    <FormField
      field-id="factor-column"
      label="Column"
    >
      <select
        id="factor-column"
        v-model="column"
        class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
      >
        <option value="">
          Choose a column
        </option>
        <option
          v-for="name in columns"
          :key="name"
          :value="name"
        >
          {{ name }}
        </option>
      </select>
    </FormField>

    <FormField
      field-id="factor-slug"
      label="Slug"
      help="A slug that already exists creates the next version of that factor, rather than
            changing it."
    >
      <input
        id="factor-slug"
        v-model="slug"
        class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
      >
    </FormField>

    <FormField
      field-id="factor-intent"
      label="Intent"
      help="Set once. A factor's intent cannot be changed afterwards."
    >
      <select
        id="factor-intent"
        v-model="intent"
        class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
      >
        <option
          v-for="value in OFFERED_FACTOR_INTENTS"
          :key="value"
          :value="value"
        >
          {{ FACTOR_INTENT_LABELS[value] }}
        </option>
      </select>
    </FormField>

    <FormField
      field-id="factor-direction"
      label="Monotonic direction"
    >
      <select
        id="factor-direction"
        v-model="direction"
        class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
      >
        <option
          v-for="(label, value) in MONOTONIC_DIRECTION_LABELS"
          :key="value"
          :value="value"
        >
          {{ label }}
        </option>
      </select>
    </FormField>

    <FormField
      v-if="rationaleRequired"
      field-id="factor-rationale"
      label="Why this direction"
      help="Required: the direction is an actuarial judgement, and the next person needs to
            know whose and why."
    >
      <textarea
        id="factor-rationale"
        v-model="rationale"
        rows="2"
        class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
      />
    </FormField>

    <button
      type="button"
      :disabled="!ready || busy"
      class="rounded-md border border-slate-300 px-3 py-1.5 text-sm disabled:opacity-50"
      @click="submit"
    >
      {{ busy ? "Creating…" : "Create factor" }}
    </button>

    <p
      v-if="created"
      class="mt-2 text-sm text-emerald-800"
    >
      Created {{ created.slug }} v{{ created.version }}.
    </p>

    <div
      v-if="problem"
      role="alert"
      class="mt-2 rounded-md border border-red-200 bg-red-50 p-3"
    >
      <p class="text-sm font-medium text-red-900">
        {{ problem.problem.title }}
      </p>
      <ul
        v-if="problem.fieldErrors.length"
        class="mt-1 space-y-1"
      >
        <li
          v-for="(error, index) in problem.fieldErrors"
          :key="index"
          class="text-sm text-red-800"
        >
          {{ error.message }}
        </li>
      </ul>
      <p
        v-else-if="problem.problem.detail"
        class="mt-1 text-sm text-red-800"
      >
        {{ problem.problem.detail }}
      </p>
    </div>
  </section>
</template>
