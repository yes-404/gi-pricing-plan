<script setup lang="ts">
/**
 * The rate table editor's route (03 §5.3): `/rating/:slug/v/:version/tables/:tableSlug`. `:slug`
 * and `:version` are the Rating Version's own (RL-1473); the table is one of its
 * `pins.rate_tables` (RL-1475 item 3), so there is no list call. The grid pages by the server's
 * cursor and never reads ahead (FR-232). A value is edited as the exact string typed (FR-10);
 * saving asks the server to preview (FR-229, FR-231), and confirming creates the next version.
 * No rule of FR-234 lives here: a refused edit shows the server's own field errors on the
 * cells they name.
 */
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";

import { ProblemError } from "@/api/problem";
import {
  confirmEdit,
  getCellPage,
  getRateTable,
  previewEdit,
  type RateTable,
  type RateTableCell,
  type RateTableDiff,
} from "@/api/rateTables";
import { getRatingVersionByRef, type RatingVersion } from "@/api/ratingVersions";
import RateTableGrid from "@/components/rating/RateTableGrid.vue";

const props = defineProps<{ slug: string; version: string; tableSlug: string }>();

/** One edited cell: its full row (what the server wants), the stored value, the typed one. */
interface Edited {
  row: RateTableCell;
  before: string;
  after: string;
}

const SEPARATOR = "\u001f";

const rating = ref<RatingVersion | null>(null);
const table = ref<RateTable | null>(null);
const rows = ref<RateTableCell[]>([]);
const nextCursor = ref<string | null>(null);
/** The cursors of the pages before this one; `undefined` is the first page. */
const history = ref<(string | undefined)[]>([]);
const currentCursor = ref<string | undefined>(undefined);
const edited = ref<Record<string, Edited>>({});
const changeNote = ref("");
const diff = ref<RateTableDiff | null>(null);
const cellErrors = ref<Record<string, string>>({});
const problem = ref<ProblemError | null>(null);
const notPinned = ref(false);
const created = ref<string | null>(null);
const loading = ref(true);
const busy = ref(false);

const tableVersion = ref(0);
const tableRef = computed(() => `${props.tableSlug}@${tableVersion.value}`);
const keyNames = computed(() => table.value?.keys.map((key) => key.name) ?? []);
const valueName = computed(() => table.value?.value.name ?? "");
const gridEdits = computed(() =>
  Object.fromEntries(Object.entries(edited.value).map(([key, entry]) => [key, entry.after])),
);
const editedCount = computed(() => Object.keys(edited.value).length);
const canReview = computed(
  () => editedCount.value > 0 && changeNote.value.trim() !== "" && !busy.value,
);

function rowKey(row: RateTableCell): string {
  return keyNames.value.map((name) => row[name]).join(SEPARATOR);
}

async function loadPage(cursor: string | undefined): Promise<void> {
  const page = await getCellPage(tableRef.value, cursor);
  rows.value = page.items;
  nextCursor.value = page.next_cursor ?? null;
  currentCursor.value = cursor;
}

async function loadTable(): Promise<void> {
  table.value = await getRateTable(tableRef.value);
  history.value = [];
  await loadPage(undefined);
}

function fail(error: unknown): void {
  if (error instanceof ProblemError) problem.value = error;
  else throw error;
}

onMounted(async () => {
  try {
    const found = await getRatingVersionByRef(props.slug, Number(props.version));
    rating.value = found;
    const pin = (found.pins?.rate_tables ?? [])
      .map((ref_) => /^rate_table:([^@]+)@(\d+)$/.exec(ref_))
      .find((match) => match?.[1] === props.tableSlug);
    if (!pin) {
      notPinned.value = true;
      return;
    }
    tableVersion.value = Number(pin[2]);
    await loadTable();
  } catch (error) {
    fail(error);
  } finally {
    loading.value = false;
  }
});

async function go(cursor: string | undefined, back: boolean): Promise<void> {
  problem.value = null;
  try {
    const here = currentCursor.value;
    await loadPage(cursor);
    if (back) history.value = history.value.slice(0, -1);
    else history.value = [...history.value, here];
  } catch (error) {
    fail(error);
  }
}

const next = (): Promise<void> => go(nextCursor.value ?? undefined, false);
const previous = (): Promise<void> => go(history.value.at(-1), true);

function onEdit(key: string, value: string): void {
  const row = rows.value.find((candidate) => rowKey(candidate) === key);
  if (!row) return;
  const before = edited.value[key]?.before ?? row[valueName.value] ?? "";
  const { [key]: _dropped, ...rest } = edited.value;
  edited.value = value === before ? rest : { ...rest, [key]: { row, before, after: value } };
  diff.value = null;
  cellErrors.value = {};
}

/** The body, in a fixed order, and the keys of its edits in that order (for 422 locations). */
function body(): { base_version: number; change_note: string; edits: RateTableCell[]; keys: string[] } {
  const keys = Object.keys(edited.value);
  return {
    base_version: tableVersion.value,
    change_note: changeNote.value.trim(),
    edits: keys.map((key) => ({ ...edited.value[key]!.row, [valueName.value]: edited.value[key]!.after })),
    keys,
  };
}

/** `edits.<index>.<value name>` → the cell at that index of the submitted edits. */
function locate(error: ProblemError, keys: string[]): void {
  const located: Record<string, string> = {};
  for (const field of error.fieldErrors) {
    const index = Number(/^edits\.(\d+)\./.exec(field.field)?.[1]);
    const key = keys[index];
    if (key !== undefined) located[key] = `${field.code}: ${field.message}`;
  }
  cellErrors.value = located;
  problem.value = Object.keys(located).length === error.fieldErrors.length ? null : error;
}

async function review(): Promise<void> {
  if (!canReview.value) return;
  const { keys, ...payload } = body();
  busy.value = true;
  problem.value = null;
  cellErrors.value = {};
  try {
    diff.value = await previewEdit(props.tableSlug, payload);
  } catch (error) {
    if (error instanceof ProblemError && error.fieldErrors.length > 0) locate(error, keys);
    else fail(error);
  } finally {
    busy.value = false;
  }
}

async function confirm(): Promise<void> {
  const { keys, ...payload } = body();
  busy.value = true;
  problem.value = null;
  try {
    const made = await confirmEdit(props.tableSlug, payload);
    tableVersion.value = made.version;
    edited.value = {};
    changeNote.value = "";
    diff.value = null;
    created.value = `Created ${props.tableSlug}@${made.version}`;
    await loadTable();
  } catch (error) {
    if (error instanceof ProblemError && error.fieldErrors.length > 0) locate(error, keys);
    else fail(error);
  } finally {
    busy.value = false;
  }
}

function discard(): void {
  diff.value = null;
}
</script>

<template>
  <section class="mx-auto max-w-5xl px-4 py-8">
    <p class="text-sm text-slate-500">
      <RouterLink
        v-if="rating"
        :to="`/rating-versions/${rating.id}`"
        class="hover:underline"
      >
        {{ rating.slug }}@{{ rating.version }}
      </RouterLink>
    </p>

    <p
      v-if="loading"
      class="mt-6 text-sm text-slate-500"
    >
      Loading…
    </p>

    <div
      v-else-if="notPinned"
      role="alert"
      class="mt-6 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-800"
    >
      This Rating Version does not pin a rate table named {{ tableSlug }}.
    </div>

    <template v-else-if="table">
      <h1 class="mt-4 text-2xl font-semibold">
        {{ tableSlug }} <span class="font-mono text-lg text-slate-500">@{{ tableVersion }}</span>
      </h1>

      <p
        v-if="created"
        aria-live="polite"
        class="mt-3 rounded-md border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800"
      >
        {{ created }}
      </p>

      <div
        v-if="problem"
        role="alert"
        class="mt-4 rounded-md border border-red-200 bg-red-50 p-4"
      >
        <p class="text-sm font-medium text-red-800">
          {{ problem.problem.title }}
        </p>
        <p class="mt-1 text-sm text-red-700">
          {{ problem.problem.detail }}
        </p>
      </div>

      <div class="mt-4 overflow-x-auto">
        <RateTableGrid
          :table="table"
          :rows="rows"
          :edits="gridEdits"
          :errors="cellErrors"
          @edit="onEdit"
        />
      </div>

      <div class="mt-3 flex items-center gap-3">
        <button
          type="button"
          class="rounded border border-slate-300 px-3 py-1 text-sm disabled:opacity-50"
          :disabled="history.length === 0"
          @click="previous"
        >
          Previous page
        </button>
        <button
          type="button"
          class="rounded border border-slate-300 px-3 py-1 text-sm disabled:opacity-50"
          :disabled="nextCursor === null"
          @click="next"
        >
          Next page
        </button>
        <span class="text-xs text-slate-500">{{ editedCount }} edited</span>
      </div>

      <div class="mt-6">
        <label
          for="change-note"
          class="mb-1 block text-sm font-medium text-slate-700"
        >Change note</label>
        <input
          id="change-note"
          v-model="changeNote"
          type="text"
          class="w-full rounded border border-slate-300 px-2 py-1 text-sm"
          @input="diff = null"
        >
        <button
          type="button"
          class="mt-3 rounded bg-sky-700 px-3 py-1.5 text-sm text-white disabled:opacity-50"
          :disabled="!canReview"
          @click="review"
        >
          Review changes
        </button>
      </div>

      <section
        v-if="diff"
        aria-label="Changes to confirm"
        class="mt-6 rounded-md border border-slate-300 p-4"
      >
        <h2 class="text-base font-semibold">
          {{ diff.changed_cells }} cell{{ diff.changed_cells === 1 ? "" : "s" }} changed
        </h2>
        <p
          v-if="diff.max_abs_change_pct != null"
          class="mt-1 text-sm text-slate-600"
        >
          Largest relative change: {{ diff.max_abs_change_pct }}%
        </p>
        <ul class="mt-3 space-y-1 font-mono text-sm">
          <li
            v-for="(entry, key) in edited"
            :key="key"
          >
            {{ keyNames.map((name) => entry.row[name]).join(" / ") }}:
            {{ entry.before }} → {{ entry.after }}
          </li>
        </ul>
        <div class="mt-4 flex gap-3">
          <button
            type="button"
            class="rounded bg-sky-700 px-3 py-1.5 text-sm text-white disabled:opacity-50"
            :disabled="busy"
            @click="confirm"
          >
            Confirm and create version
          </button>
          <button
            type="button"
            class="rounded border border-slate-300 px-3 py-1.5 text-sm"
            @click="discard"
          >
            Keep editing
          </button>
        </div>
      </section>
    </template>
  </section>
</template>
