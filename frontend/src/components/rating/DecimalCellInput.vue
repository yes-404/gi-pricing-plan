<script setup lang="ts">
/**
 * One exact-decimal cell (FR-10, FR-21): a text input that hands the string typed to its
 * parent and does nothing else with it. The value is never a number, so a decimal past a
 * float's precision survives; the pattern is a syntax check only (bounds and coverage are
 * the server's, FR-234, so they are defined once).
 */
import { computed, ref, useId, watch } from "vue";

const props = defineProps<{
  modelValue: string;
  /** The server's error for this cell (FR-234); shown beside the input. */
  invalid?: string;
  /** Whole numbers only: money in minor units and counts (FR-10). */
  integer?: boolean;
  /** The accessible name, e.g. the row's key. */
  label?: string;
}>();
const emit = defineEmits<{ "update:modelValue": [value: string] }>();

const text = ref(props.modelValue);
watch(
  () => props.modelValue,
  (value) => {
    text.value = value;
  },
);

const DECIMAL = /^-?\d+(\.\d+)?$/;
const INTEGER = /^-?\d+$/;
const syntaxError = computed(
  () => text.value !== "" && !(props.integer ? INTEGER : DECIMAL).test(text.value),
);
const isInvalid = computed(() => syntaxError.value || Boolean(props.invalid));
const errorId = useId();

function onInput(event: Event): void {
  text.value = (event.target as HTMLInputElement).value;
  emit("update:modelValue", text.value);
}
</script>

<template>
  <span class="inline-flex flex-col">
    <input
      type="text"
      :inputmode="integer ? 'numeric' : 'decimal'"
      :value="text"
      :aria-label="label"
      :aria-invalid="isInvalid ? 'true' : 'false'"
      :aria-describedby="invalid ? errorId : undefined"
      autocomplete="off"
      class="w-28 rounded border px-2 py-1 text-right font-mono text-sm"
      :class="isInvalid ? 'border-red-600' : 'border-slate-300'"
      @input="onInput"
    >
    <span
      v-if="invalid"
      :id="errorId"
      class="text-xs text-red-700"
    >{{ invalid }}</span>
  </span>
</template>
