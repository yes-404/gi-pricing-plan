<script setup lang="ts">
/**
 * The structural diff against another version (FR-219). The server computes the diff; this
 * shows what it returned and emits it so the designer can mark the nodes.
 */
import { computed, ref } from "vue";

import { ProblemError } from "@/api/problem";
import { getAlgorithmDiff, type AlgorithmDiff } from "@/api/ratingAlgorithms";

const props = defineProps<{ slug: string; version: number }>();
const emit = defineEmits<{ diff: [value: AlgorithmDiff | null] }>();

const against = ref<number | null>(props.version - 1);
const result = ref<AlgorithmDiff | null>(null);
const message = ref("");
const busy = ref(false);

const hasChanges = computed(
  () =>
    result.value !== null &&
    (result.value.added_steps.length > 0 ||
      result.value.removed_steps.length > 0 ||
      result.value.changed_steps.length > 0 ||
      result.value.repointed_tables.length > 0 ||
      result.value.input_contract_changed ||
      result.value.outputs_changed),
);

function clear(): void {
  result.value = null;
  message.value = "";
  emit("diff", null);
}

function onInput(event: Event): void {
  const raw = (event.target as HTMLInputElement).value;
  against.value = raw === "" ? null : Number(raw);
  if (against.value === null) clear();
}

async function compare(): Promise<void> {
  if (against.value === null || !Number.isInteger(against.value) || against.value < 1) return;
  busy.value = true;
  message.value = "";
  try {
    result.value = await getAlgorithmDiff(props.slug, props.version, against.value);
    emit("diff", result.value);
  } catch (error) {
    result.value = null;
    emit("diff", null);
    message.value =
      error instanceof ProblemError && error.code === "NOT_FOUND"
        ? "Version not found"
        : "The comparison could not be loaded";
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <section
    v-if="version > 1"
    aria-labelledby="diff-title"
    class="space-y-2"
  >
    <h3
      id="diff-title"
      class="text-sm font-medium text-slate-700"
    >
      Compare with another version
    </h3>
    <div class="flex items-end gap-2">
      <div class="flex-1">
        <label
          for="diff-against"
          class="mb-1 block text-sm text-slate-700"
        >Compare with version</label>
        <input
          id="diff-against"
          type="number"
          min="1"
          :value="against ?? ''"
          class="w-full rounded-md border border-slate-300 px-2 py-1 text-sm"
          @input="onInput"
        >
      </div>
      <button
        type="button"
        class="rounded-md border border-slate-300 bg-white px-3 py-1 text-sm"
        :disabled="busy || against === null"
        @click="compare"
      >
        Compare
      </button>
    </div>
    <p
      v-if="message"
      role="alert"
      class="text-sm text-red-800"
    >
      {{ message }}
    </p>
    <div
      v-if="result"
      aria-label="Differences"
      role="region"
      class="text-sm text-slate-800"
    >
      <p v-if="!hasChanges">
        No structural differences.
      </p>
      <template v-if="result.removed_steps.length > 0">
        <h4 class="font-medium">
          Removed
        </h4>
        <ul class="list-disc pl-5">
          <li
            v-for="id in result.removed_steps"
            :key="id"
          >
            {{ id }}
          </li>
        </ul>
      </template>
      <template v-if="result.repointed_tables.length > 0">
        <h4 class="font-medium">
          Re-pointed tables
        </h4>
        <ul class="list-disc pl-5">
          <li
            v-for="r in result.repointed_tables"
            :key="`${r.step_id}-${r.field}`"
          >
            {{ r.step_id }}: {{ r.before }} → {{ r.after }}
          </li>
        </ul>
      </template>
      <p v-if="result.input_contract_changed">
        The input contract changed.
      </p>
      <p v-if="result.outputs_changed">
        The declared outputs changed.
      </p>
    </div>
  </section>
</template>
