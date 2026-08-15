<script setup lang="ts">
import { computed, onMounted, ref, toRaw } from "vue";
import { RouterLink } from "vue-router";

import {
  forbidsModelling,
  getDataset,
  listVersions,
  putDictionary,
  type DataDictionaryEntry,
  type Dataset,
} from "@/api/datasets";
import { ProblemError } from "@/api/problem";
import type { DatasetVersion } from "@/api/versions";

const props = defineProps<{ slug: string }>();

const dataset = ref<Dataset | null>(null);
const versions = ref<DatasetVersion[]>([]);
const nextCursor = ref<string | null>(null);
const loading = ref(true);
const problem = ref<ProblemError | null>(null);

const editing = ref(false);
const draft = ref<Record<string, DataDictionaryEntry>>({});
const saving = ref(false);
const saveError = ref<string | null>(null);

const columns = computed(() => Object.keys(dataset.value?.data_dictionary ?? {}).sort());
const forbidden = computed(() =>
  columns.value.filter((c) => forbidsModelling(dataset.value?.data_dictionary?.[c])),
);

const STATUS_TONE: Record<string, string> = {
  draft: "bg-slate-100 text-slate-700",
  validating: "bg-amber-100 text-amber-900",
  validated: "bg-emerald-100 text-emerald-900",
  archived: "bg-slate-200 text-slate-600",
};

async function load(cursor?: string): Promise<void> {
  loading.value = true;
  problem.value = null;
  try {
    if (!cursor) dataset.value = await getDataset(props.slug);
    const page = await listVersions(props.slug, { cursor });
    versions.value = cursor ? [...versions.value, ...page.items] : page.items;
    nextCursor.value = page.next_cursor ?? null;
  } catch (error) {
    if (error instanceof ProblemError) problem.value = error;
    else throw error;
  } finally {
    loading.value = false;
  }
}

function startEditing(): void {
  // A deep copy through `toRaw`: the editor must not mutate what the screen is still
  // showing, or a cancelled edit would silently stick. `structuredClone` on the reactive
  // value itself throws `DataCloneError` — a Proxy is not structured-cloneable, and the
  // error names the object rather than the reactivity, so it reads like bad data.
  draft.value = structuredClone(toRaw(dataset.value?.data_dictionary ?? {}));
  saveError.value = null;
  editing.value = true;
}

async function save(): Promise<void> {
  saving.value = true;
  saveError.value = null;
  try {
    dataset.value = await putDictionary(props.slug, draft.value);
    editing.value = false;
  } catch (error) {
    saveError.value =
      error instanceof ProblemError
        ? `${error.problem.title}. ${error.problem.detail ?? ""}`.trim()
        : "The dictionary could not be saved.";
  } finally {
    saving.value = false;
  }
}

onMounted(() => void load());
</script>

<template>
  <section>
    <header class="mb-5">
      <p class="text-sm text-slate-500">
        <RouterLink
          to="/data"
          class="hover:underline"
        >
          Datasets
        </RouterLink>
      </p>
      <h1 class="mt-1 text-xl font-semibold tracking-tight">
        {{ dataset?.name || slug }}
      </h1>
      <p
        v-if="dataset"
        class="mt-1 text-sm text-slate-500"
      >
        <span class="font-mono">{{ dataset.slug }}</span>
        <template v-if="dataset.line_of_business">
          · {{ dataset.line_of_business }}
        </template>
        <template v-if="dataset.territory">
          · {{ dataset.territory }}
        </template>
        · {{ dataset.currency }}
      </p>
    </header>

    <p
      v-if="loading && !dataset"
      class="text-sm text-slate-500"
    >
      Loading…
    </p>

    <div
      v-else-if="problem"
      role="alert"
      class="rounded-md border border-red-200 bg-red-50 p-4"
    >
      <p class="font-medium text-red-900">
        {{ problem.problem.title }}
      </p>
      <p
        v-if="problem.problem.detail"
        class="mt-1 text-sm text-red-800"
      >
        {{ problem.problem.detail }}
      </p>
      <p
        v-if="problem.traceId"
        class="mt-2 font-mono text-xs text-red-700"
      >
        trace {{ problem.traceId }}
      </p>
    </div>

    <template v-else-if="dataset">
      <p
        v-if="forbidden.length"
        class="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-900"
      >
        <strong>{{ forbidden.length }}</strong>
        column{{ forbidden.length === 1 ? "" : "s" }} may not be modelled on
        (FR-OVR-9): <span class="font-mono">{{ forbidden.join(", ") }}</span>.
      </p>

      <section class="mt-6">
        <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Versions
        </h2>
        <table
          aria-label="Versions"
          class="mt-2 w-full text-left text-sm"
        >
          <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th
                scope="col"
                class="py-2 font-medium"
              >
                Version
              </th>
              <th
                scope="col"
                class="py-2 font-medium"
              >
                Status
              </th>
              <th
                scope="col"
                class="py-2 text-right font-medium"
              >
                Exposure
              </th>
              <th
                scope="col"
                class="py-2 font-medium"
              >
                Created
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in versions"
              :key="row.id"
              class="border-b border-slate-100"
            >
              <td class="py-2">
                <RouterLink
                  :to="`/data/${slug}/v/${row.version}`"
                  class="font-medium hover:underline"
                >
                  v{{ row.version }}
                </RouterLink>
              </td>
              <td class="py-2">
                <span
                  :class="['rounded px-2 py-0.5 text-xs font-medium',
                           STATUS_TONE[row.status] ?? 'bg-slate-100']"
                >{{ row.status }}</span>
              </td>
              <td class="py-2 text-right tabular-nums text-slate-600">
                {{ row.totals?.exposure_years ?? "—" }}
              </td>
              <td class="py-2 text-slate-600">
                {{ new Date(row.created_at).toLocaleDateString() }}
              </td>
            </tr>
          </tbody>
        </table>
        <button
          v-if="nextCursor"
          type="button"
          class="mt-3 rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-100"
          @click="load(nextCursor ?? undefined)"
        >
          Load more
        </button>
      </section>

      <section class="mt-8">
        <div class="flex items-center gap-3">
          <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Data dictionary — {{ columns.length }}
          </h2>
          <button
            v-if="!editing"
            type="button"
            class="rounded-md border border-slate-300 px-2.5 py-1 text-xs hover:bg-slate-50"
            @click="startEditing"
          >
            Edit
          </button>
        </div>

        <p
          v-if="editing"
          class="mt-2 text-xs text-slate-600"
        >
          Saving replaces the whole dictionary and is recorded in the audit log with its
          previous state.
        </p>
        <p
          v-if="saveError"
          role="alert"
          class="mt-2 text-sm text-red-800"
        >
          {{ saveError }}
        </p>

        <table
          aria-label="Data dictionary"
          class="mt-2 w-full text-left text-sm"
        >
          <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th
                scope="col"
                class="py-2 font-medium"
              >
                Column
              </th>
              <th
                scope="col"
                class="py-2 font-medium"
              >
                Description
              </th>
              <th
                scope="col"
                class="py-2 font-medium"
              >
                Semantic type
              </th>
              <th
                scope="col"
                class="py-2 font-medium"
              >
                PII class
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="column in columns"
              :key="column"
              class="border-b border-slate-100"
            >
              <td class="py-2 font-mono text-xs">
                {{ column }}
              </td>
              <td class="py-2">
                <input
                  v-if="editing && draft[column]"
                  v-model="draft[column]!.description"
                  :aria-label="`Description for ${column}`"
                  class="w-full rounded border border-slate-300 px-1.5 py-0.5 text-sm"
                >
                <span
                  v-else
                  class="text-slate-700"
                >{{ dataset.data_dictionary?.[column]?.description || "—" }}</span>
              </td>
              <td class="py-2 text-slate-600">
                {{ dataset.data_dictionary?.[column]?.semantic_type ?? "—" }}
              </td>
              <td class="py-2">
                <select
                  v-if="editing && draft[column]"
                  v-model="draft[column]!.pii_class"
                  :aria-label="`PII class for ${column}`"
                  class="rounded border border-slate-300 px-1.5 py-0.5 text-sm"
                >
                  <option value="none">
                    none
                  </option>
                  <option value="pseudonymous_key">
                    pseudonymous_key
                  </option>
                  <option value="quasi_identifier">
                    quasi_identifier
                  </option>
                  <option value="direct_identifier">
                    direct_identifier
                  </option>
                  <option value="special_category">
                    special_category
                  </option>
                </select>
                <span
                  v-else
                  :class="forbidsModelling(dataset.data_dictionary?.[column])
                    ? 'font-medium text-red-800' : 'text-slate-600'"
                >{{ dataset.data_dictionary?.[column]?.pii_class ?? "none" }}</span>
              </td>
            </tr>
          </tbody>
        </table>

        <div
          v-if="editing"
          class="mt-3 flex gap-2"
        >
          <button
            type="button"
            class="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50"
            @click="editing = false"
          >
            Cancel
          </button>
          <button
            type="button"
            class="rounded-md bg-slate-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50"
            :disabled="saving"
            @click="save"
          >
            {{ saving ? "Saving…" : "Save dictionary" }}
          </button>
        </div>
      </section>
    </template>
  </section>
</template>
