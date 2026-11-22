<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import type { components } from "@/api/generated/schema";
import { ProblemError } from "@/api/problem";
import { getSystemStatus, type SystemStatus } from "@/api/systemStatus";

/**
 * `07` §5.3's `/admin/status`: component health, the schema version, queue depths, cache
 * hit rates and blob store usage, deployment-wide (§4.6, FR-443, FR-444).
 *
 * Any role that holds `settings:read` may open it, which is every built-in role
 * (decision, #1505 comment 7060618416, answer 1); the platform answers 403 to a caller with
 * no role. A `null` in `schema_version`, `queues` or `blob_store` means the database could
 * not be read (comment 7070124577) and is shown in words, never as blank, empty or 0.
 */
const status = ref<SystemStatus | null>(null);
const loading = ref(true);
const problem = ref<ProblemError | null>(null);

// The component state is the generated `ComponentStatus` (`up` or `down`), not a restated union.
type ComponentStatus = components["schemas"]["ComponentStatus"];

const UNREADABLE = "could not be read";

onMounted(async () => {
  try {
    status.value = await getSystemStatus();
  } catch (error) {
    if (error instanceof ProblemError) problem.value = error;
    else throw error;
  } finally {
    loading.value = false;
  }
});

/** hits / (hits + misses), or `null` when there has been no read (shown as "no reads yet"). */
function rate(hits: number, misses: number): string | null {
  const total = hits + misses;
  if (total === 0) return null;
  return `${((hits / total) * 100).toFixed(1)} %`;
}

const caches = computed(() =>
  (status.value?.caches ?? []).map((cache) => ({ ...cache, rate: rate(cache.hits, cache.misses) })),
);

function badge(state: ComponentStatus): string {
  return state === "up"
    ? "bg-green-100 text-green-900"
    : "bg-red-100 text-red-900";
}
</script>

<template>
  <section>
    <header class="mb-5">
      <h1 class="text-xl font-semibold tracking-tight">
        System status
      </h1>
      <p class="mt-1 text-sm text-slate-500">
        Deployment-wide. The cache counts are those of the API process that answered.
      </p>
    </header>

    <p
      v-if="loading"
      class="text-sm text-slate-500"
    >
      Loading system status...
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
    </div>

    <div
      v-else-if="status"
      class="space-y-6"
    >
      <p class="text-sm">
        Overall:
        <span
          data-testid="overall-status"
          :class="['rounded px-2 py-0.5 font-medium', badge(status.status)]"
        >{{ status.status }}</span>
      </p>

      <div>
        <h2 class="mb-2 text-sm font-semibold">
          Components
        </h2>
        <ul class="space-y-1 text-sm">
          <li
            v-for="component in status.components"
            :key="component.name"
            class="flex items-center gap-3"
          >
            <span class="w-24 font-mono">{{ component.name }}</span>
            <span :class="['rounded px-2 py-0.5 font-medium', badge(component.status)]">{{ component.status }}</span>
            <span
              v-if="component.detail"
              class="text-slate-600"
            >{{ component.detail }}</span>
          </li>
        </ul>
      </div>

      <p
        class="text-sm"
        data-testid="schema-version"
      >
        Schema version:
        <span
          v-if="status.schema_version === null"
          class="font-medium text-red-800"
        >{{ UNREADABLE }}</span>
        <span
          v-else
          class="font-mono"
        >{{ status.schema_version }}</span>
      </p>

      <div data-testid="queues">
        <h2 class="mb-2 text-sm font-semibold">
          Job queues
        </h2>
        <p
          v-if="status.queues === null"
          class="text-sm font-medium text-red-800"
        >
          Queue depths {{ UNREADABLE }}.
        </p>
        <p
          v-else-if="status.queues.length === 0"
          class="text-sm text-slate-600"
        >
          Nothing queued.
        </p>
        <table
          v-else
          class="text-left text-sm"
        >
          <thead class="text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th class="pr-6 font-medium">
                Kind
              </th>
              <th class="pr-6 font-medium">
                Status
              </th>
              <th class="font-medium">
                Depth
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="queue in status.queues"
              :key="`${queue.kind}/${queue.status}`"
            >
              <td class="pr-6 font-mono">
                {{ queue.kind }}
              </td>
              <td class="pr-6">
                {{ queue.status }}
              </td>
              <td>{{ queue.depth }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div data-testid="blob-store">
        <h2 class="mb-2 text-sm font-semibold">
          Blob store
        </h2>
        <p
          v-if="status.blob_store === null"
          class="text-sm font-medium text-red-800"
        >
          Blob store usage {{ UNREADABLE }}.
        </p>
        <p
          v-else
          class="text-sm"
        >
          {{ status.blob_store.objects }} objects, {{ status.blob_store.bytes }} bytes
        </p>
      </div>

      <div>
        <h2 class="mb-2 text-sm font-semibold">
          Caches
        </h2>
        <p
          v-if="caches.length === 0"
          class="text-sm text-slate-600"
        >
          No cache reports.
        </p>
        <table
          v-else
          class="text-left text-sm"
        >
          <thead class="text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th class="pr-6 font-medium">
                Cache
              </th>
              <th class="pr-6 font-medium">
                Hits
              </th>
              <th class="pr-6 font-medium">
                Misses
              </th>
              <th class="font-medium">
                Hit rate
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="cache in caches"
              :key="cache.name"
            >
              <td class="pr-6 font-mono">
                {{ cache.name }}
              </td>
              <td class="pr-6">
                {{ cache.hits }}
              </td>
              <td class="pr-6">
                {{ cache.misses }}
              </td>
              <td>{{ cache.rate ?? "no reads yet" }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>
