<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";

import {
  exportAudit,
  listAudit,
  verifyChain,
  type AuditEventListing,
  type AuditFilters,
  type ChainVerification,
} from "@/api/audit";
import { ProblemError } from "@/api/problem";

/** `total_estimate` is capped (`00` §5.2): past the cap it is "1,000+", not a total. */
const COUNT_CAP = 1000;

const form = reactive({ actor: "", entity: "", action: "", from: "", to: "", q: "" });
/** The filters the list on screen was loaded with: export and verify use these, not the form. */
const applied = ref<AuditFilters>({});

const events = ref<AuditEventListing[]>([]);
const totalEstimate = ref(0);
const nextCursor = ref<string | null>(null);
const loading = ref(true);
const problem = ref<ProblemError | null>(null);

const verification = ref<ChainVerification | null>(null);
const verifying = ref(false);
const exporting = ref(false);

/** An empty field is no filter; a date-time field is sent as an instant. */
function toFilters(): AuditFilters {
  const text = (value: string): string | undefined => value.trim() || undefined;
  const instant = (value: string): string | undefined =>
    value ? new Date(value).toISOString() : undefined;
  return {
    actor: text(form.actor),
    entity: text(form.entity),
    action: text(form.action),
    from: instant(form.from),
    to: instant(form.to),
    q: text(form.q),
  };
}

function refuse(error: unknown): void {
  if (error instanceof ProblemError) problem.value = error;
  else throw error;
}

async function load(cursor?: string): Promise<void> {
  loading.value = true;
  problem.value = null;
  try {
    const page = await listAudit(applied.value, cursor);
    events.value = cursor ? [...events.value, ...page.items] : page.items;
    nextCursor.value = page.next_cursor ?? null;
    totalEstimate.value = page.total_estimate;
  } catch (error) {
    refuse(error);
  } finally {
    loading.value = false;
  }
}

function apply(): void {
  applied.value = toFilters();
  verification.value = null;
  void load();
}

/** A row's entity becomes the entity filter: the log read around one artifact. */
function showEntity(entity: string): void {
  form.entity = entity;
  apply();
}

const hasRange = computed(() => applied.value.from !== undefined || applied.value.to !== undefined);

async function verify(whole: boolean): Promise<void> {
  verifying.value = true;
  problem.value = null;
  try {
    verification.value = await verifyChain(
      whole ? {} : { from: applied.value.from, to: applied.value.to },
    );
  } catch (error) {
    refuse(error);
  } finally {
    verifying.value = false;
  }
}

async function download(format: "csv" | "json"): Promise<void> {
  exporting.value = true;
  problem.value = null;
  try {
    const text = await exportAudit(applied.value, format);
    const type = format === "csv" ? "text/csv" : "application/x-ndjson";
    const url = URL.createObjectURL(new Blob([text], { type }));
    const link = document.createElement("a");
    link.href = url;
    link.download = format === "csv" ? "audit.csv" : "audit.jsonl";
    link.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    refuse(error);
  } finally {
    exporting.value = false;
  }
}

onMounted(() => void load());
</script>

<template>
  <section>
    <header class="mb-6 flex items-baseline justify-between">
      <h1 class="text-xl font-semibold tracking-tight">
        Audit log
      </h1>
      <p
        v-if="!loading && !problem"
        class="text-sm text-slate-500"
      >
        {{ totalEstimate >= COUNT_CAP ? "1,000+" : totalEstimate }}
        {{ totalEstimate === 1 ? "event" : "events" }}
      </p>
    </header>

    <form
      class="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-3"
      @submit.prevent="apply"
    >
      <label class="text-sm">
        Actor (user id)
        <input
          v-model="form.actor"
          class="mt-1 w-full rounded border border-slate-300 px-2 py-1"
        >
      </label>
      <label class="text-sm">
        Entity
        <input
          v-model="form.entity"
          placeholder="model:motor-freq@2"
          class="mt-1 w-full rounded border border-slate-300 px-2 py-1"
        >
      </label>
      <label class="text-sm">
        Action
        <input
          v-model="form.action"
          placeholder="model.approved"
          class="mt-1 w-full rounded border border-slate-300 px-2 py-1"
        >
      </label>
      <label class="text-sm">
        From
        <input
          v-model="form.from"
          type="datetime-local"
          class="mt-1 w-full rounded border border-slate-300 px-2 py-1"
        >
      </label>
      <label class="text-sm">
        To
        <input
          v-model="form.to"
          type="datetime-local"
          class="mt-1 w-full rounded border border-slate-300 px-2 py-1"
        >
      </label>
      <label class="text-sm">
        Justification text
        <input
          v-model="form.q"
          class="mt-1 w-full rounded border border-slate-300 px-2 py-1"
        >
      </label>
      <div class="sm:col-span-3">
        <button
          type="submit"
          class="rounded bg-slate-900 px-3 py-1 text-sm text-white"
        >
          Apply filters
        </button>
      </div>
    </form>

    <div
      class="mb-6 rounded-md border border-slate-200 bg-white p-4"
      aria-live="polite"
    >
      <h2 class="text-sm font-medium">
        Hash chain
      </h2>
      <!-- FR-373: say what the chain defends against and what it does not. -->
      <p class="mt-1 text-xs text-slate-500">
        The chain is tamper-evident against modification below the application: an edited or
        removed event breaks every hash after it. It cannot show that nothing was removed from
        the end of the log, or by someone who can rewrite every hash.
      </p>
      <div class="mt-3 flex gap-2">
        <button
          type="button"
          class="rounded border border-slate-300 px-3 py-1 text-sm"
          :disabled="verifying || !hasRange"
          @click="verify(false)"
        >
          Verify range shown
        </button>
        <button
          type="button"
          class="rounded border border-slate-300 px-3 py-1 text-sm"
          :disabled="verifying"
          @click="verify(true)"
        >
          Verify whole chain
        </button>
      </div>
      <p
        v-if="verification && verification.intact"
        class="mt-3 text-sm text-green-800"
      >
        Chain intact: {{ verification.events_checked }} events checked
        <template v-if="verification.first_sequence != null">
          (sequence {{ verification.first_sequence }} to {{ verification.last_sequence }},
          {{ verification.whole_chain ? "whole chain" : "range only" }}).
        </template>
      </p>
      <p
        v-else-if="verification"
        role="alert"
        class="mt-3 text-sm font-medium text-red-800"
      >
        Chain broken at sequence {{ verification.broken_at_sequence }}: {{ verification.reason }}
      </p>
    </div>

    <div class="mb-3 flex gap-2">
      <button
        type="button"
        class="rounded border border-slate-300 px-3 py-1 text-sm"
        :disabled="exporting"
        @click="download('csv')"
      >
        Export CSV
      </button>
      <button
        type="button"
        class="rounded border border-slate-300 px-3 py-1 text-sm"
        :disabled="exporting"
        @click="download('json')"
      >
        Export JSON Lines
      </button>
      <p class="self-center text-xs text-slate-500">
        Exports the events shown. JSON Lines is the form to recompute hashes from.
      </p>
    </div>

    <div
      v-if="problem"
      role="alert"
      class="mb-3 rounded-md border border-red-200 bg-red-50 p-4"
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
      v-if="loading && events.length === 0"
      class="text-sm text-slate-500"
    >
      Loading…
    </p>
    <p
      v-else-if="!problem && events.length === 0"
      class="text-sm text-slate-500"
    >
      No events match.
    </p>
    <table
      v-else-if="events.length > 0"
      class="w-full text-left text-sm"
    >
      <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
        <tr>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Seq
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            At (UTC)
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Actor
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Action
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Entity
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Justification
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="event in events"
          :key="event.id"
          class="border-b border-slate-100"
        >
          <td class="py-2">
            {{ event.sequence }}
          </td>
          <td class="py-2">
            {{ event.at }}
          </td>
          <td class="py-2">
            {{ event.actor.display ?? event.actor.kind }}
          </td>
          <td class="py-2 font-mono text-xs">
            {{ event.action }}
            <!-- The stored name is always shown as stored; a pre-rename return says what it is
                 called today (FR-370: stored events are never rewritten). -->
            <span
              v-if="event.current_action"
              class="ml-1 font-sans text-slate-500"
            >
              (stored name; now written {{ event.current_action }})
            </span>
          </td>
          <td class="py-2">
            <button
              type="button"
              class="font-mono text-xs underline"
              @click="showEntity(event.entity_ref)"
            >
              {{ event.entity_ref }}
            </button>
            <!-- Q12 (a): every entity links to history; a non-artifact ref is the view's 422. -->
            <RouterLink
              :to="`/artifacts/${encodeURIComponent(event.entity_ref)}/history`"
              class="ml-2 text-xs text-slate-600 underline"
            >
              history
            </RouterLink>
          </td>
          <td class="py-2">
            {{ event.justification }}
          </td>
        </tr>
      </tbody>
    </table>

    <button
      v-if="nextCursor"
      type="button"
      class="mt-4 rounded border border-slate-300 px-3 py-1 text-sm"
      :disabled="loading"
      @click="load(nextCursor ?? undefined)"
    >
      Load more
    </button>
  </section>
</template>
