<script setup lang="ts">
/**
 * The bulk-operation dialog (FR-233): the four operations a rate table takes as one step, each
 * recorded with its parameters. It posts the generated `BulkOperationRequest` and reads the
 * generated `RateTableVersion` (`SL-1669` typed the route); every rule about the values (the
 * decimals, the columns, the bounds) is the platform's, so a refusal is shown as it came (FR-234).
 */
import { reactive, ref } from "vue";

import { ProblemError } from "@/api/problem";
import { bulkOperation, type RateTableVersion } from "@/api/rateTables";

import { BULK_KINDS, buildBulkRequest, type BulkField, type BulkKind } from "./bulkOperation";

const props = defineProps<{ tableRef: string }>();
const emit = defineEmits<{ created: [RateTableVersion] }>();

const LABELS: Record<BulkField, string> = {
  percentage: "Percentage",
  filter: "Key filter",
  floor: "Floor",
  cap: "Cap",
  base_level: "Base level",
};
const MULTILINE: readonly BulkField[] = ["filter", "base_level"];

const kind = ref<BulkKind>("uplift_table");
const values = reactive<Partial<Record<BulkField, string>>>({});
const busy = ref(false);
const problem = ref("");
const created = ref("");

function fieldsOf(chosen: BulkKind): readonly BulkField[] {
  return BULK_KINDS.find((entry) => entry.kind === chosen)?.fields ?? [];
}

async function apply(): Promise<void> {
  problem.value = "";
  created.value = "";
  let request;
  try {
    request = buildBulkRequest(kind.value, values);
  } catch (error) {
    problem.value = error instanceof Error ? error.message : String(error);
    return;
  }
  busy.value = true;
  try {
    const made = await bulkOperation(props.tableRef, request);
    created.value = `Created ${made.slug}@${made.version}`;
    emit("created", made);
  } catch (error) {
    if (!(error instanceof ProblemError)) throw error;
    problem.value = error.problem.detail ?? error.problem.title;
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <section
    role="dialog"
    aria-labelledby="bulk-title"
    class="rounded-md border border-slate-300 p-4"
  >
    <h2
      id="bulk-title"
      class="text-base font-semibold"
    >
      Bulk operation
    </h2>
    <div class="mt-3">
      <label
        for="bulk-kind"
        class="mb-1 block text-sm font-medium text-slate-700"
      >Operation</label>
      <select
        id="bulk-kind"
        v-model="kind"
        class="rounded border border-slate-500 px-2 py-1 text-sm"
      >
        <option
          v-for="entry in BULK_KINDS"
          :key="entry.kind"
          :value="entry.kind"
        >
          {{ entry.label }}
        </option>
      </select>
    </div>
    <div
      v-for="field in fieldsOf(kind)"
      :key="field"
      class="mt-3"
    >
      <label
        :for="`bulk-${field}`"
        class="mb-1 block text-sm font-medium text-slate-700"
      >{{ LABELS[field] }}</label>
      <textarea
        v-if="MULTILINE.includes(field)"
        :id="`bulk-${field}`"
        v-model="values[field]"
        rows="3"
        placeholder="area: A, B"
        class="w-full rounded border border-slate-500 px-2 py-1 font-mono text-sm"
      />
      <input
        v-else
        :id="`bulk-${field}`"
        v-model="values[field]"
        type="text"
        inputmode="decimal"
        autocomplete="off"
        class="rounded border border-slate-500 px-2 py-1 font-mono text-sm"
      >
    </div>
    <p
      v-if="problem"
      role="alert"
      class="mt-3 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800"
    >
      {{ problem }}
    </p>
    <p
      role="status"
      :class="created ? 'mt-3 rounded-md border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800' : ''"
    >
      {{ created }}
    </p>
    <button
      type="button"
      class="mt-4 rounded bg-sky-700 px-3 py-1.5 text-sm text-white disabled:opacity-50"
      :disabled="busy"
      @click="apply"
    >
      Apply
    </button>
  </section>
</template>
