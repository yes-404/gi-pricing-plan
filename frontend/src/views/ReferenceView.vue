<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import { ProblemError } from "@/api/problem";
import {
  coverage,
  listRows,
  listTables,
  listVersions,
  lookup,
  type ReferenceLookup,
  type ReferenceRow,
  type ReferenceTable,
  type ReferenceTableVersion,
} from "@/api/reference";

/**
 * `01` §5.3's `/reference`: table list, version timeline, effective-date viewer, lookup
 * debugger — one screen, because they are one question. "Why did this quote get area 13?"
 * is answered by picking the table, the version that was pinned, and the date.
 */
const tables = ref<ReferenceTable[]>([]);
const selected = ref<string | null>(null);
const versions = ref<ReferenceTableVersion[]>([]);
const pinned = ref<number | null>(null);
const rows = ref<ReferenceRow[]>([]);
const asAt = ref("");
const loading = ref(true);
const problem = ref<ProblemError | null>(null);

const lookupKey = ref("");
const lookupResult = ref<ReferenceLookup | null>(null);
const lookupMiss = ref<string | null>(null);

const table = computed(() => tables.value.find((t) => t.slug === selected.value) ?? null);
const version = computed(() => versions.value.find((v) => v.version === pinned.value) ?? null);

function fail(error: unknown): void {
  if (error instanceof ProblemError) problem.value = error;
  else throw error;
}

onMounted(async () => {
  try {
    tables.value = await listTables();
    selected.value = tables.value[0]?.slug ?? null;
  } catch (error) {
    fail(error);
  } finally {
    loading.value = false;
  }
});

watch(selected, async (slug) => {
  versions.value = [];
  pinned.value = null;
  rows.value = [];
  lookupResult.value = null;
  lookupMiss.value = null;
  if (!slug) return;
  try {
    versions.value = await listVersions(slug);
    // The newest **published** version, not merely the newest: a draft cannot be pinned by
    // rating (FR-DATA-32), so opening on one would show a version no quote can have used.
    pinned.value = (versions.value.find((v) => v.status === "published")
      ?? versions.value[0])?.version ?? null;
  } catch (error) {
    fail(error);
  }
});

watch([selected, pinned, asAt], async () => {
  const slug = selected.value;
  const version = pinned.value;
  rows.value = [];
  if (!slug || version === null) return;
  try {
    rows.value = await listRows(slug, version, { asAt: asAt.value || undefined });
  } catch (error) {
    fail(error);
  }
});

async function debug(): Promise<void> {
  lookupResult.value = null;
  lookupMiss.value = null;
  if (!selected.value || !lookupKey.value || !asAt.value) return;
  try {
    lookupResult.value = await lookup(selected.value, {
      key: lookupKey.value,
      asAt: asAt.value,
      version: pinned.value ?? undefined,
    });
  } catch (error) {
    // A miss is the answer most likely to look like a bug, and the server's detail
    // explains it in terms of the half-open interval. Showing it beats restating it.
    if (error instanceof ProblemError) lookupMiss.value = error.problem.detail ?? error.problem.title;
    else throw error;
  }
}
</script>

<template>
  <section>
    <header class="mb-5">
      <h1 class="text-xl font-semibold tracking-tight">
        Reference tables
      </h1>
      <p class="mt-1 text-sm text-slate-500">
        Effective-dated lookups. A version is immutable and pinned by id — rating never
        resolves "the latest", because "latest" at scoring time is a different answer each
        month.
      </p>
    </header>

    <p
      v-if="loading"
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

    <p
      v-else-if="!tables.length"
      class="text-sm text-slate-600"
    >
      No reference tables are declared in this workspace.
    </p>

    <template v-else>
      <table
        aria-label="Reference tables"
        class="w-full text-left text-sm"
      >
        <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th
              scope="col"
              class="py-2 font-medium"
            >
              Table
            </th>
            <th
              scope="col"
              class="py-2 font-medium"
            >
              Keyed by
            </th>
            <th
              scope="col"
              class="py-2 font-medium"
            >
              Versions
            </th>
            <th
              scope="col"
              class="py-2 font-medium"
            >
              Pinnable
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in tables"
            :key="row.id"
            :class="['border-b border-slate-100',
                     row.slug === selected ? 'bg-slate-50' : '']"
          >
            <td class="py-2">
              <button
                type="button"
                class="font-mono text-xs hover:underline"
                @click="selected = row.slug"
              >
                {{ row.slug }}
              </button>
              <p
                v-if="row.description"
                class="mt-0.5 text-xs text-slate-500"
              >
                {{ row.description }}
              </p>
            </td>
            <td class="py-2 font-mono text-xs text-slate-600">
              {{ (row.key_columns ?? []).join(", ") }}
            </td>
            <td class="py-2">
              {{ row.version_count }}
            </td>
            <!-- Null is the state that matters: a table whose versions are all drafts
                 cannot be pinned at all, and a version number here regardless would say
                 it is usable when nothing has been published. -->
            <td class="py-2">
              <span v-if="row.latest_published_version">v{{ row.latest_published_version }}</span>
              <span
                v-else
                class="text-amber-800"
              >no published version</span>
            </td>
          </tr>
        </tbody>
      </table>

      <template v-if="table">
        <section class="mt-8">
          <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
            {{ table.slug }} — versions
          </h2>
          <ul class="mt-2 space-y-1">
            <li
              v-for="item in versions"
              :key="item.id"
            >
              <button
                type="button"
                :class="['w-full rounded border px-3 py-2 text-left text-sm',
                         item.version === pinned
                           ? 'border-slate-400 bg-slate-50'
                           : 'border-slate-200 hover:bg-slate-50']"
                @click="pinned = item.version"
              >
                <span class="font-medium">v{{ item.version }}</span>
                <span class="ml-2 text-xs text-slate-500">{{ item.status }}</span>
                <span class="ml-2 text-xs text-slate-500">{{ item.row_count }} rows</span>
                <span class="ml-2 font-mono text-xs text-slate-600">
                  {{ coverage(item) }}
                </span>
                <span
                  v-if="item.source_note"
                  class="ml-2 text-xs text-slate-500"
                >{{ item.source_note }}</span>
              </button>
            </li>
          </ul>
        </section>

        <section class="mt-8">
          <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Effective-date viewer
          </h2>
          <p
            v-if="version"
            class="mt-1 text-xs text-slate-500"
          >
            Reading <strong>v{{ version.version }}</strong> only. The date filters the rows
            of this version; it never selects a different one.
          </p>
          <label class="mt-2 block text-sm">
            <span class="text-slate-600">As at</span>
            <input
              v-model="asAt"
              type="date"
              class="ml-2 rounded border border-slate-300 px-2 py-1"
            >
            <button
              v-if="asAt"
              type="button"
              class="ml-2 rounded border border-slate-300 px-2 py-0.5 text-xs hover:bg-slate-50"
              @click="asAt = ''"
            >
              Show the version whole
            </button>
          </label>

          <table
            aria-label="Reference rows"
            class="mt-3 w-full text-left text-sm"
          >
            <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th
                  scope="col"
                  class="py-2 font-medium"
                >
                  Key
                </th>
                <th
                  scope="col"
                  class="py-2 font-medium"
                >
                  Payload
                </th>
                <th
                  scope="col"
                  class="py-2 font-medium"
                >
                  Effective from
                </th>
                <th
                  scope="col"
                  class="py-2 font-medium"
                >
                  Until (exclusive)
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(row, index) in rows"
                :key="`${row.key}-${index}`"
                class="border-b border-slate-100"
              >
                <td class="py-2 font-mono text-xs">
                  {{ row.key }}
                </td>
                <td class="py-2 font-mono text-xs text-slate-600">
                  {{ JSON.stringify(row.payload) }}
                </td>
                <td class="py-2 font-mono text-xs">
                  {{ row.effective_from }}
                </td>
                <!-- "Until (exclusive)", and "open-ended" rather than a blank: the interval
                     is half-open, so a row ending 2026-07-01 does not cover that day. A
                     reader checking why a quote changed on the 1st is checking this cell. -->
                <td class="py-2 font-mono text-xs">
                  {{ row.effective_to ?? "open-ended" }}
                </td>
              </tr>
            </tbody>
          </table>
          <p
            v-if="!rows.length"
            class="mt-2 text-sm text-slate-500"
          >
            No rows in force on that date.
          </p>
        </section>

        <section class="mt-8">
          <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Lookup debugger
          </h2>
          <p class="mt-1 text-xs text-slate-500">
            For debugging (FR-DATA-31) — what does this table say about this key on this
            date? Rating resolves a reference through a pinned version id and never asks
            this question at scoring time.
          </p>
          <div class="mt-2 flex flex-wrap items-end gap-2">
            <label class="text-sm">
              <span class="text-slate-600">Key</span>
              <input
                v-model="lookupKey"
                class="ml-2 rounded border border-slate-300 px-2 py-1 font-mono"
              >
            </label>
            <button
              type="button"
              :disabled="!lookupKey || !asAt"
              class="rounded bg-slate-900 px-3 py-1.5 text-sm text-white disabled:opacity-50"
              @click="debug"
            >
              Look up
            </button>
            <span
              v-if="!asAt"
              class="text-sm text-slate-500"
            >Pick a date above — a lookup with no date has no answer.</span>
          </div>

          <p
            v-if="lookupResult"
            class="mt-3 rounded-md border border-slate-200 bg-slate-50 px-3 py-2 font-mono text-xs"
          >
            v{{ lookupResult.version }} · {{ JSON.stringify(lookupResult.payload) }} ·
            {{ lookupResult.effective_from }} → {{ lookupResult.effective_to ?? "open-ended" }}
          </p>
          <p
            v-else-if="lookupMiss"
            class="mt-3 rounded-md border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-950"
          >
            {{ lookupMiss }}
          </p>
        </section>
      </template>
    </template>
  </section>
</template>
