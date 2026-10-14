<script setup lang="ts">
/**
 * One typed per-quote error, rendered distinctly (03 FR-255): contract violation, reference
 * miss, table miss and model failure each get their own heading, so an actuary sees which of
 * the five kinds of failure this was. The fifth, a constraint decline, is not an error at all:
 * it is a successful result with `outcome: declined` (FR-256) and is `QuoteOutcome`'s.
 * Any other code is shown under its own code and detail, never as a generic failure.
 */
import { computed } from "vue";

import type { ProblemError } from "@/api/problem";

const props = defineProps<{ error: ProblemError }>();

const CATEGORIES: Readonly<Record<string, { heading: string; hint: string }>> = {
  INPUT_CONTRACT_VIOLATION: {
    heading: "Contract violation",
    hint: "An input is missing, mistyped, out of range or outside its domain.",
  },
  REFERENCE_LOOKUP_MISS: {
    heading: "Reference miss",
    hint: "A reference-table key had no row in force at the effective date.",
  },
  RATE_TABLE_MISS: {
    heading: "Table miss",
    hint: "A rate table had no row for this quote's key.",
  },
  MODEL_CALL_FAILED: {
    heading: "Model failure",
    hint: "A pinned model could not score this quote.",
  },
};

const category = computed(() => CATEGORIES[props.error.code]);
</script>

<template>
  <div
    role="alert"
    class="rounded-md border border-red-200 bg-red-50 p-4"
  >
    <p class="text-sm font-medium text-red-800">
      {{ category?.heading ?? error.problem.title }}
      <span class="ml-2 font-mono text-xs">{{ error.code }}</span>
    </p>
    <p
      v-if="category"
      class="mt-1 text-xs text-red-700"
    >
      {{ category.hint }}
    </p>
    <p class="mt-1 text-sm text-red-700">
      {{ error.problem.detail }}
    </p>
    <ul
      v-if="error.fieldErrors.length > 0"
      class="mt-2 list-disc pl-5 text-sm text-red-700"
    >
      <li
        v-for="(fieldError, index) in error.fieldErrors"
        :key="index"
      >
        {{ fieldError.field }}: {{ fieldError.message }}
      </li>
    </ul>
    <p
      v-if="error.traceId"
      class="mt-2 font-mono text-xs text-red-700"
    >
      trace {{ error.traceId }}
    </p>
  </div>
</template>
