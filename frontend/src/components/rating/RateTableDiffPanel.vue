<script setup lang="ts">
/**
 * A rate table version's changed cells against another version (FR-231, FR-232): the previous
 * one or the seed, with the exposure weight behind each cell when a validated portfolio Dataset
 * Version is named. Only changed cells are served, one cursor page at a time, never read ahead;
 * the first request for a comparison may answer 202 with the Job that builds it, which is polled
 * and then read as a page. Shade follows the size of the relative change and the direction is
 * written out beside it, so colour is never the only signal (`03` §5.3).
 */
import { computed, ref } from "vue";

import { waitForJob } from "@/api/jobs";
import { ProblemError } from "@/api/problem";
import { getDiffCells, isJob, type RateTableDiffCell, type RateTableDiffCellPage } from "@/api/rateTables";

import { shadeChange } from "./diffShading";

const props = withDefaults(
  defineProps<{ tableRef: string; pollAttempts?: number; pollIntervalMs?: number }>(),
  { pollAttempts: 60, pollIntervalMs: 1000 },
);

type Stage = "idle" | "loading" | "waiting" | "ready" | "stalled" | "failed";

const against = ref<"previous" | "seed">("previous");
const portfolio = ref("");
const stage = ref<Stage>("idle");
const message = ref("");
const items = ref<RateTableDiffCell[]>([]);
const nextCursor = ref<string | null>(null);
/** The cursors of the pages before this one; `undefined` is the first page. */
const history = ref<(string | undefined)[]>([]);
const currentCursor = ref<string | undefined>(undefined);
/** Whether the page on show was asked for with a portfolio, so the weight column matches it. */
const weighted = ref(false);

const keyNames = computed(() => Object.keys(items.value[0]?.key ?? {}));

/** The query for a page: nothing is sent that was not asked for. */
function query(cursor: string | undefined): { against: string; portfolio?: string; cursor?: string } {
  const named = portfolio.value.trim();
  return {
    against: against.value,
    ...(named === "" ? {} : { portfolio: named }),
    ...(cursor === undefined ? {} : { cursor }),
  };
}

async function readPage(cursor: string | undefined): Promise<RateTableDiffCellPage | null> {
  const answer = await getDiffCells(props.tableRef, query(cursor));
  if (!isJob(answer)) return answer;
  stage.value = "waiting";
  const job = await waitForJob(answer.id, { attempts: props.pollAttempts, intervalMs: props.pollIntervalMs });
  if (job.status === "succeeded") {
    const built = await getDiffCells(props.tableRef, query(cursor));
    return isJob(built) ? null : built;
  }
  if (job.status === "failed" || job.status === "cancelled") {
    stage.value = "failed";
    message.value = job.error?.message ?? `The comparison job ${job.status}.`;
  } else {
    stage.value = "stalled";
    message.value = "The comparison is still running. Show changes again in a moment.";
  }
  return null;
}

async function load(cursor: string | undefined): Promise<boolean> {
  stage.value = "loading";
  message.value = "";
  try {
    const page = await readPage(cursor);
    if (page === null) return false;
    items.value = page.items;
    nextCursor.value = page.next_cursor ?? null;
    currentCursor.value = cursor;
    weighted.value = portfolio.value.trim() !== "";
    stage.value = "ready";
    return true;
  } catch (error) {
    if (!(error instanceof ProblemError)) throw error;
    stage.value = "failed";
    message.value = error.problem.detail ?? error.problem.title;
    return false;
  }
}

async function show(): Promise<void> {
  history.value = [];
  await load(undefined);
}

async function next(): Promise<void> {
  const here = currentCursor.value;
  if (await load(nextCursor.value ?? undefined)) history.value = [...history.value, here];
}

async function previous(): Promise<void> {
  if (await load(history.value.at(-1))) history.value = history.value.slice(0, -1);
}

const SHADES = [
  "",
  "bg-amber-50",
  "bg-amber-100",
  "bg-amber-200",
  "bg-amber-300",
] as const;
const COOLS = [
  "",
  "bg-sky-50",
  "bg-sky-100",
  "bg-sky-200",
  "bg-sky-300",
] as const;

function shadeClass(rel: string | null): string {
  const shade = shadeChange(rel);
  return shade.direction === "down" ? COOLS[shade.step] : SHADES[shade.step];
}
</script>

<template>
  <section
    aria-label="Changes against another version"
    class="rounded-md border border-slate-300 p-4"
  >
    <h2 class="text-base font-semibold">
      Changes
    </h2>
    <div class="mt-3 flex flex-wrap items-end gap-4">
      <div>
        <label
          for="diff-against"
          class="mb-1 block text-sm font-medium text-slate-700"
        >Compare against</label>
        <select
          id="diff-against"
          v-model="against"
          class="rounded border border-slate-300 px-2 py-1 text-sm"
        >
          <option value="previous">
            Previous version
          </option>
          <option value="seed">
            Seed
          </option>
        </select>
      </div>
      <div>
        <label
          for="diff-portfolio"
          class="mb-1 block text-sm font-medium text-slate-700"
        >Portfolio Dataset Version</label>
        <input
          id="diff-portfolio"
          v-model="portfolio"
          type="text"
          autocomplete="off"
          class="rounded border border-slate-300 px-2 py-1 font-mono text-sm"
        >
      </div>
      <button
        type="button"
        class="rounded bg-sky-700 px-3 py-1.5 text-sm text-white disabled:opacity-50"
        :disabled="stage === 'loading' || stage === 'waiting'"
        @click="show"
      >
        Show changes
      </button>
    </div>

    <p
      v-if="stage === 'loading' || stage === 'waiting'"
      aria-live="polite"
      class="mt-3 text-sm text-slate-500"
    >
      {{ stage === "waiting" ? "Building the comparison…" : "Loading…" }}
    </p>
    <p
      v-else-if="stage === 'stalled'"
      aria-live="polite"
      class="mt-3 text-sm text-slate-600"
    >
      {{ message }}
    </p>
    <p
      v-else-if="stage === 'failed'"
      role="alert"
      class="mt-3 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800"
    >
      {{ message }}
    </p>

    <template v-if="stage === 'ready'">
      <p
        v-if="items.length === 0"
        class="mt-3 text-sm text-slate-600"
      >
        No cells differ.
      </p>
      <div
        v-else
        class="mt-3 overflow-x-auto"
      >
        <table class="min-w-full border-collapse text-sm">
          <thead>
            <tr>
              <th
                v-for="name in keyNames"
                :key="name"
                scope="col"
                class="border-b border-slate-300 px-3 py-2 text-left font-semibold"
              >
                {{ name }}
              </th>
              <th
                scope="col"
                class="border-b border-slate-300 px-3 py-2 text-left font-semibold"
              >
                Change
              </th>
              <th
                scope="col"
                class="border-b border-slate-300 px-3 py-2 text-right font-semibold"
              >
                Before
              </th>
              <th
                scope="col"
                class="border-b border-slate-300 px-3 py-2 text-right font-semibold"
              >
                After
              </th>
              <th
                scope="col"
                class="border-b border-slate-300 px-3 py-2 text-right font-semibold"
              >
                Absolute
              </th>
              <th
                scope="col"
                class="border-b border-slate-300 px-3 py-2 text-right font-semibold"
              >
                Relative
              </th>
              <th
                v-if="weighted"
                scope="col"
                class="border-b border-slate-300 px-3 py-2 text-right font-semibold"
              >
                Exposure weight
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in items"
              :key="keyNames.map((name) => item.key[name]).join('\u001f')"
            >
              <th
                v-for="(name, index) in keyNames"
                :key="name"
                :scope="index === 0 ? 'row' : undefined"
                :role="index === 0 ? 'rowheader' : undefined"
                class="border-b border-slate-100 px-3 py-1 text-left font-normal"
              >
                {{ item.key[name] }}
              </th>
              <td class="border-b border-slate-100 px-3 py-1">
                {{ item.change }}
              </td>
              <td class="border-b border-slate-100 px-3 py-1 text-right font-mono">
                {{ item.baseline_value ?? "—" }}
              </td>
              <td class="border-b border-slate-100 px-3 py-1 text-right font-mono">
                {{ item.current_value ?? "—" }}
              </td>
              <td class="border-b border-slate-100 px-3 py-1 text-right font-mono">
                {{ item.abs_change ?? "—" }}
              </td>
              <td
                class="border-b border-slate-100 px-3 py-1 text-right font-mono"
                :class="shadeClass(item.rel_change_pct ?? null)"
              >
                <span :data-direction="shadeChange(item.rel_change_pct ?? null).direction">{{
                  shadeChange(item.rel_change_pct ?? null).label
                }}</span>
              </td>
              <td
                v-if="weighted"
                class="border-b border-slate-100 px-3 py-1 text-right font-mono"
              >
                {{ item.weight ?? "—" }}
              </td>
            </tr>
          </tbody>
        </table>
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
      </div>
    </template>
  </section>
</template>
