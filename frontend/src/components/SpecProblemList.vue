<script setup lang="ts">
/**
 * Every reason a spec cannot be fitted, rendered as a list (`02` §5.1, FR-MODEL-44,
 * FR-MODEL-81).
 *
 * **All of them, never the first.** `SpecValidation`'s own docstring in the contract says
 * why: "Reported as a list rather than raised as the first failure. A spec builder that
 * surfaced one error at a time would make a ten-factor spec a ten-round conversation."
 *
 * The `LABEL` map is keyed `Record<SpecProblemKind, string>` off the generated union, so
 * the compiler enumerates the eleven members rather than a human remembering to. That is
 * not a style choice here — `SpecProblemKind`'s contract docstring states the requirement
 * directly: "A closed set, **because the frontend renders each differently** and an open
 * string would make that a guess about wording." A `Record<string, string>` would let a
 * twelfth kind render as a blank heading with a message under it, which is the shape of
 * the `DatasetStatus` defect W6b-3 fixed.
 *
 * The label is a heading, not a replacement for `message`: the backend writes the message
 * "in terms the caller can act on" (`SpecProblem`'s docstring) and this component never
 * paraphrases it. `subject` is rendered as given and **not** routed to a form field —
 * it is a workspace setting key in the complexity case (`modelling.max_factor_count`),
 * not a field name, so a subject→field map would be invented here and wrong the first
 * time a new kind arrived.
 */
import type { SpecProblem, SpecProblemKind } from "@/api/modelSpecs";

defineProps<{ problems: readonly SpecProblem[] }>();

const LABEL: Record<SpecProblemKind, string> = {
  dataset_not_validated: "Dataset version is not validated",
  factor_missing: "Factor not found",
  factor_prohibited: "Factor may not be modelled",
  factor_unresolvable: "Factor reference cannot be resolved",
  split_missing: "No split named",
  split_invalid: "Split is not usable",
  response_missing: "No response column",
  offset_missing: "Offset required and absent",
  model_offset_unresolvable: "Model offset cannot be resolved",
  complexity_limit: "Beyond the workspace complexity limit",
  objective_unsupported: "Objective does not apply to this response",
};
</script>

<template>
  <ul
    v-if="problems.length"
    class="space-y-2"
  >
    <li
      v-for="(problem, index) in problems"
      :key="`${problem.kind}-${index}`"
      class="rounded-md border border-amber-200 bg-amber-50 p-3"
    >
      <p class="text-sm font-medium text-amber-900">
        {{ LABEL[problem.kind] }}
      </p>
      <p class="mt-1 text-sm text-amber-800">
        {{ problem.message }}
      </p>
      <p
        v-if="problem.subject"
        class="mt-1 font-mono text-xs text-amber-700"
      >
        {{ problem.subject }}
      </p>
    </li>
  </ul>
</template>
