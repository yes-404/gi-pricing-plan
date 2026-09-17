<script setup lang="ts">
import { ref, watch } from "vue";

import type { RuleResult } from "@/api/validation";

const props = defineProps<{ result: RuleResult | null; submitting: boolean; error: string | null }>();
const emit = defineEmits<{ confirm: [justification: string]; cancel: [] }>();

const justification = ref("");

watch(
  () => props.result,
  () => {
    justification.value = "";
  },
);

/**
 * FR-46: the justification is mandatory, and the platform refuses an empty one with
 * `VALIDATION_FAILED`. Disabling the button is a courtesy, not the control — the check
 * that matters is the server's, and this only avoids a round trip to be told so.
 */
function submit(): void {
  if (justification.value.trim()) emit("confirm", justification.value.trim());
}
</script>

<template>
  <div
    v-if="result"
    class="fixed inset-0 z-10 flex items-center justify-center bg-slate-900/40 p-4"
    role="dialog"
    aria-modal="true"
    aria-labelledby="ack-title"
  >
    <div class="w-full max-w-lg rounded-lg bg-white p-6 shadow-xl">
      <h2
        id="ack-title"
        class="text-lg font-semibold"
      >
        Acknowledge “{{ result.rule_slug }}”
      </h2>
      <p class="mt-2 text-sm text-slate-600">
        This records that a Pricing Actuary has read the warning and accepts modelling on
        this data. It is written to the audit log with your name and cannot be withdrawn.
      </p>
      <p
        v-if="result.detail"
        class="mt-3 rounded bg-amber-50 px-3 py-2 text-sm text-amber-900"
      >
        {{ result.detail }}
      </p>

      <label
        class="mt-4 block text-sm font-medium"
        for="justification"
      >
        Justification <span class="font-normal text-slate-500">(required)</span>
      </label>
      <textarea
        id="justification"
        v-model="justification"
        rows="3"
        class="mt-1 w-full rounded-md border border-slate-300 p-2 text-sm"
        placeholder="Why is it acceptable to model on this data?"
      />

      <p
        v-if="error"
        role="alert"
        class="mt-2 text-sm text-red-800"
      >
        {{ error }}
      </p>

      <div class="mt-5 flex justify-end gap-2">
        <button
          type="button"
          class="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50"
          @click="emit('cancel')"
        >
          Cancel
        </button>
        <button
          type="button"
          class="rounded-md bg-amber-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-amber-700 disabled:opacity-50"
          :disabled="!justification.trim() || submitting"
          @click="submit"
        >
          {{ submitting ? "Recording…" : "Acknowledge" }}
        </button>
      </div>
    </div>
  </div>
</template>
