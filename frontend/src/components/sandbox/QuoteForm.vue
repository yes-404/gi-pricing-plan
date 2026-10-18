<script setup lang="ts">
/**
 * The quote form, generated from the algorithm's input contract (03 FR-213, §5.3).
 *
 * One control per declared input, chosen by its declared type; the Quote Context's own
 * `purpose` and `effective_date` beside them. It types what the actuary entered
 * (`buildInputs`) and emits it — the platform's contract check is the only rule engine, so a
 * range or domain violation comes back as `INPUT_CONTRACT_VIOLATION`, not as a second copy
 * of the check here.
 */
import { computed, reactive, ref } from "vue";

import type { QuotePurpose } from "@/api/score";
import FormField from "@/components/FormField.vue";

import {
  buildInputs,
  type ContractField,
  fieldHint,
  type QuoteFormSubmit,
  type RawValue,
} from "./quoteForm";

const props = defineProps<{
  fields: readonly ContractField[];
  submitting?: boolean;
}>();

const emit = defineEmits<{ submit: [QuoteFormSubmit] }>();

const PURPOSES: readonly QuotePurpose[] = [
  "what_if",
  "new_business",
  "renewal",
  "mid_term_adjustment",
  "cancellation",
];

const raw = reactive<Record<string, RawValue>>({});
const purpose = ref<QuotePurpose>("what_if");
const effectiveDate = ref(new Date().toISOString().slice(0, 10));
const problems = ref<Record<string, string>>({});

const hints = computed(() =>
  Object.fromEntries(props.fields.map((field) => [field.name, fieldHint(field)])),
);

function submit(): void {
  const built = buildInputs(props.fields, raw);
  problems.value = { ...built.problems };
  if (Object.keys(built.problems).length > 0) return;
  emit("submit", {
    inputs: built.inputs,
    purpose: purpose.value,
    effective_date: effectiveDate.value,
  });
}
</script>

<template>
  <form
    class="max-w-xl"
    novalidate
    @submit.prevent="submit"
  >
    <FormField
      field-id="quote-purpose"
      label="Purpose"
      help="what_if is a test price, never a quotable one (FR-251)."
    >
      <select
        id="quote-purpose"
        v-model="purpose"
        class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
      >
        <option
          v-for="option in PURPOSES"
          :key="option"
          :value="option"
        >
          {{ option }}
        </option>
      </select>
    </FormField>

    <FormField
      field-id="quote-effective-date"
      label="Effective date"
    >
      <input
        id="quote-effective-date"
        v-model="effectiveDate"
        type="date"
        required
        class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
      >
    </FormField>

    <FormField
      v-for="field in fields"
      :key="field.name"
      :field-id="`quote-input-${field.name}`"
      :label="field.name"
      :help="hints[field.name] ?? ''"
    >
      <input
        v-if="field.type === 'bool'"
        :id="`quote-input-${field.name}`"
        v-model="raw[field.name]"
        type="checkbox"
      >
      <select
        v-else-if="field.type === 'enum'"
        :id="`quote-input-${field.name}`"
        v-model="raw[field.name]"
        class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
      >
        <option value="">
          {{ field.nullable ? "(none)" : "Choose…" }}
        </option>
        <option
          v-for="value in field.domain ?? []"
          :key="value"
          :value="value"
        >
          {{ value }}
        </option>
      </select>
      <input
        v-else
        :id="`quote-input-${field.name}`"
        v-model="raw[field.name]"
        :type="field.type === 'date' ? 'date' : 'text'"
        :inputmode="field.type === 'int' ? 'numeric' : field.type === 'decimal' ? 'decimal' : undefined"
        autocomplete="off"
        class="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
        :aria-invalid="problems[field.name] ? 'true' : undefined"
        :aria-describedby="problems[field.name] ? `quote-input-${field.name}-problem` : undefined"
      >
      <p
        v-if="problems[field.name]"
        :id="`quote-input-${field.name}-problem`"
        role="alert"
        class="mt-1 text-xs text-red-700"
      >
        {{ problems[field.name] }}
      </p>
    </FormField>

    <button
      type="submit"
      :disabled="submitting"
      class="rounded-md bg-sky-700 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
    >
      {{ submitting ? "Scoring…" : "Score quote" }}
    </button>
  </form>
</template>
