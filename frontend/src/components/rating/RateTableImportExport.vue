<script setup lang="ts">
/**
 * CSV export and import of a rate table version (FR-235). Import is two steps on the same file:
 * the platform checks it against the version (keys, types, coverage — the strict round trip) and
 * answers the diff it would make; only a confirmation creates the version, and choosing another
 * file drops the preview so a diff for one file is never confirmed for another.
 */
import { computed, ref } from "vue";

import { ProblemError } from "@/api/problem";
import {
  confirmImport,
  exportCsv,
  previewImport,
  type ImportPreview,
  type RateTableVersion,
} from "@/api/rateTables";

const props = defineProps<{ tableRef: string }>();
const emit = defineEmits<{ created: [RateTableVersion] }>();

const file = ref<File | null>(null);
const preview = ref<ImportPreview | null>(null);
const busy = ref(false);
const problem = ref("");
const created = ref("");

const changed = computed(() => preview.value?.diff.changed_cells ?? 0);

function refuse(error: unknown): void {
  if (!(error instanceof ProblemError)) throw error;
  problem.value = error.problem.detail ?? error.problem.title;
}

async function download(): Promise<void> {
  problem.value = "";
  busy.value = true;
  try {
    const text = await exportCsv(props.tableRef);
    const url = URL.createObjectURL(new Blob([text], { type: "text/csv" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = `${props.tableRef}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    refuse(error);
  } finally {
    busy.value = false;
  }
}

function choose(event: Event): void {
  file.value = (event.target as HTMLInputElement).files?.[0] ?? null;
  preview.value = null;
  problem.value = "";
  created.value = "";
}

async function check(): Promise<void> {
  if (!file.value) return;
  problem.value = "";
  busy.value = true;
  try {
    preview.value = await previewImport(props.tableRef, file.value);
  } catch (error) {
    refuse(error);
  } finally {
    busy.value = false;
  }
}

async function confirm(): Promise<void> {
  if (!file.value) return;
  problem.value = "";
  busy.value = true;
  try {
    const made = await confirmImport(props.tableRef, file.value);
    created.value = `Created ${made.slug}@${made.version}`;
    preview.value = null;
    emit("created", made);
  } catch (error) {
    refuse(error);
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <section
    aria-label="CSV import and export"
    class="rounded-md border border-slate-300 p-4"
  >
    <h2 class="text-base font-semibold">
      CSV
    </h2>
    <div class="mt-3 flex flex-wrap items-end gap-4">
      <button
        type="button"
        class="rounded border border-slate-300 px-3 py-1.5 text-sm disabled:opacity-50"
        :disabled="busy"
        @click="download"
      >
        Export CSV
      </button>
      <div>
        <label
          for="import-file"
          class="mb-1 block text-sm font-medium text-slate-700"
        >CSV file</label>
        <input
          id="import-file"
          type="file"
          accept=".csv,text/csv"
          class="text-sm"
          @change="choose"
        >
      </div>
      <button
        type="button"
        class="rounded bg-sky-700 px-3 py-1.5 text-sm text-white disabled:opacity-50"
        :disabled="file === null || busy"
        @click="check"
      >
        Check file
      </button>
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

    <div
      v-if="preview"
      class="mt-4"
    >
      <h3 class="text-sm font-semibold">
        {{ changed }} cell{{ changed === 1 ? "" : "s" }} would change
      </h3>
      <p
        v-if="preview.diff.max_abs_change_pct != null"
        class="mt-1 text-sm text-slate-600"
      >
        Largest relative change: {{ preview.diff.max_abs_change_pct }}%
      </p>
      <p class="mt-1 text-sm text-slate-600">
        {{ preview.created_by_import.filename }} passed the round-trip check against
        {{ preview.created_by_import.applied_to }}.
      </p>
      <button
        type="button"
        class="mt-3 rounded bg-sky-700 px-3 py-1.5 text-sm text-white disabled:opacity-50"
        :disabled="busy"
        @click="confirm"
      >
        Confirm and create version
      </button>
    </div>
  </section>
</template>
