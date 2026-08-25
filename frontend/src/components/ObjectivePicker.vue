<script setup lang="ts">
/**
 * The GBM arm's objective: one of FR-MODEL-26's builtins, or an approved-enough Custom
 * Objective (FR-MODEL-38, FR-MODEL-44).
 *
 * Emits a `GbmFunctionRef`, whose validator makes the two arms mutually exclusive —
 * `kind: "builtin"` carries a `name` and no `ref`, `kind: "custom"` a `ref` and no `name`,
 * because "the fit path would have to choose, and two runs could choose differently".
 *
 * **GBM only.** `GlmSpec` has no `custom_objective_ref`; FR-MODEL-87 records it "absent
 * entirely" with Phase 1b as owner, and `test_contracts.py` allowlists the divergence
 * deliberately. A governed gap, not a §0 disagreement — and nothing here hints that custom
 * objectives are coming to the GLM arm, because that would assert a schedule no
 * requirement carries.
 *
 * **Not the artifact library.** No usage count, no certificate, no submit or certify —
 * `CustomObjective` carries `usage_count` on the row and this deliberately ignores it.
 * Those belong to the library screen.
 */
import { computed, onMounted, ref } from "vue";

import {
  BUILTIN_GBM_OBJECTIVES,
  type GbmFunctionRef,
  type ResponseKind,
} from "@/api/modelSpecs";
import {
  FITTABLE_OBJECTIVE_STATUSES,
  listObjectives,
  type CustomObjective,
} from "@/api/objectives";

const props = defineProps<{
  modelValue: GbmFunctionRef;
  /** The spec's response. Custom objectives declare which they apply to (FR-MODEL-44). */
  response: ResponseKind | "";
  /** `xgboost` or `lightgbm` — the spec's `model_type`, an applicability axis too. */
  backend: string;
}>();

const emit = defineEmits<{ "update:modelValue": [GbmFunctionRef] }>();

const objectives = ref<CustomObjective[]>([]);
const truncated = ref(false);
const failed = ref(false);

/**
 * **The three fittable statuses are a set, not a ladder — and that is what a reader gets
 * wrong.**
 *
 * Written here, at the code that renders them, because the mistake it prevents is a
 * labelling mistake made at this spot. `objectives.py`:160-161 permits `REVIEW →
 * {APPROVED, CERTIFIED}`, so an objective in review can return to certified, and neither
 * `draft` nor `certified` may jump straight to `approved`. Anyone assuming a sequence
 * writes "almost approved" for `review` and is wrong in both directions.
 *
 * So the option labels are the **status names themselves**, carrying no ordering, and the
 * only distinction drawn anywhere below is the one that is real and actionable:
 * **approved, or not yet**. That single note covers `certified` and `review` identically,
 * which is precisely the relationship they have to one another — none.
 */

/** Whether R4 will let a Model built on this reach `approved`. */
function approvable(objective: CustomObjective): boolean {
  return objective.status === "approved";
}

/**
 * Applicable to the spec as it stands (FR-MODEL-44).
 *
 * Filtered here rather than by the server because the route cannot: its query is `status`,
 * `slug`, `cursor`, `limit`. That is OQ-MODEL-35, and `truncated` is how this picker
 * admits the consequence rather than hiding it.
 *
 * With no response chosen, nothing is offered — not everything. A custom objective
 * "declares no `response`" is itself a refusal the validator raises, so offering objectives
 * before the response is chosen would offer specs known to be refused. **That falls out of
 * the response filter rather than needing its own guard**: an empty response is in no
 * objective's `responses`, so the same line excludes everything. An `if (!props.response)
 * return []` early return was written here first and removed — a §13 mutation disabling it
 * changed no test, because the filter below was already doing the work, and a line whose
 * removal is undetectable is a line asserting something untrue about why the code is
 * correct.
 */
const applicable = computed(() =>
  objectives.value.filter(
    (objective) =>
      FITTABLE_OBJECTIVE_STATUSES.includes(objective.status as never)
      && objective.applicability.responses.includes(props.response as ResponseKind)
      && objective.applicability.backends.includes(props.backend as never),
  ),
);

const selection = computed({
  get: () =>
    props.modelValue.kind === "custom"
      ? `custom:${props.modelValue.ref}`
      : `builtin:${props.modelValue.name}`,
  set: (value: string) => {
    const [kind, ...rest] = value.split(":");
    const target = rest.join(":");
    emit(
      "update:modelValue",
      kind === "custom"
        ? { kind: "custom", ref: target }
        : { kind: "builtin", name: target },
    );
  },
});

onMounted(async () => {
  try {
    const result = await listObjectives();
    objectives.value = result.items;
    truncated.value = result.truncated;
  } catch {
    // A custom-objective lookup that fails must not take the builtin arm with it: the
    // builtins need no network at all, and a picker that renders nothing because an
    // optional list could not load is worse than one that renders less.
    failed.value = true;
  }
});
</script>

<template>
  <div>
    <select
      id="gbm-objective"
      v-model="selection"
      class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
    >
      <optgroup label="Built in">
        <option
          v-for="name in BUILTIN_GBM_OBJECTIVES"
          :key="name"
          :value="`builtin:${name}`"
        >
          {{ name }}
        </option>
      </optgroup>

      <optgroup
        v-if="applicable.length"
        label="Custom"
      >
        <option
          v-for="objective in applicable"
          :key="objective.id"
          :value="`custom:custom_objective:${objective.slug}@${objective.version}`"
        >
          {{ objective.slug }}@{{ objective.version }} — {{ objective.status }}
        </option>
      </optgroup>
    </select>

    <!--
      One statement covering `certified` and `review` identically, because their
      relationship to each other is none — see the FITTABLE comment. It names the
      consequence rather than a position in a sequence.
    -->
    <p
      v-if="applicable.some((o) => !approvable(o))"
      class="mt-1 text-xs text-slate-500"
    >
      A custom objective that is not yet <code>approved</code> can be fitted, but a model
      using it cannot be approved until the objective is.
    </p>

    <p
      v-if="!response"
      class="mt-1 text-xs text-slate-500"
    >
      Choose a response to see custom objectives — applicability is declared against it.
    </p>

    <p
      v-if="truncated"
      class="mt-1 text-xs text-amber-700"
    >
      More custom objectives exist than were loaded, so this list may be incomplete.
    </p>

    <p
      v-if="failed"
      class="mt-1 text-xs text-amber-700"
    >
      Custom objectives could not be loaded. Built-in objectives are unaffected.
    </p>
  </div>
</template>
