<script setup lang="ts">
import { computed, ref, watch } from "vue";

import { getArtifactHistory, type ArtifactHistory } from "@/api/audit";
import { ProblemError } from "@/api/problem";

const props = defineProps<{ artifactRef: string }>();

const history = ref<ArtifactHistory | null>(null);
const loading = ref(true);
const problem = ref<ProblemError | null>(null);

/** `type:slug@version`, split on the last `@`; versions are sequential from 1 (ID-2). */
const parts = computed(() => {
  const at = props.artifactRef.lastIndexOf("@");
  const version = Number(props.artifactRef.slice(at + 1));
  return at > 0 && Number.isInteger(version) && version >= 1
    ? { base: props.artifactRef.slice(0, at), version }
    : null;
});
const previous = computed(() =>
  parts.value && parts.value.version > 1 ? `${parts.value.base}@${parts.value.version - 1}` : null,
);
const next = computed(() =>
  parts.value ? `${parts.value.base}@${parts.value.version + 1}` : null,
);

/** What the user is told for the two refusals this view expects; any other is shown as sent. */
const refusal = computed(() => {
  if (problem.value?.code === "NOT_FOUND") return "No recorded history for this artifact version.";
  if (problem.value?.code === "VALIDATION_FAILED") return "This reference is not an artifact.";
  return null;
});

function show(value: unknown): string {
  return typeof value === "string" ? value : JSON.stringify(value);
}

async function load(): Promise<void> {
  loading.value = true;
  problem.value = null;
  history.value = null;
  try {
    history.value = await getArtifactHistory(props.artifactRef);
  } catch (error) {
    if (error instanceof ProblemError) problem.value = error;
    else throw error;
  } finally {
    loading.value = false;
  }
}

watch(() => props.artifactRef, () => void load(), { immediate: true });
</script>

<template>
  <section>
    <header class="mb-6">
      <h1 class="text-xl font-semibold tracking-tight">
        History of <span class="font-mono">{{ artifactRef }}</span>
      </h1>
      <nav
        v-if="parts"
        class="mt-2 flex gap-4 text-sm"
        aria-label="Versions"
      >
        <RouterLink
          v-if="previous"
          :to="`/artifacts/${encodeURIComponent(previous)}/history`"
          class="underline"
        >
          Previous version
        </RouterLink>
        <RouterLink
          v-if="next"
          :to="`/artifacts/${encodeURIComponent(next)}/history`"
          class="underline"
        >
          Next version
        </RouterLink>
      </nav>
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
        {{ refusal ?? problem.problem.title }}
      </p>
      <p
        v-if="!refusal && problem.problem.detail"
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

    <ol
      v-else-if="history"
      class="space-y-4"
    >
      <li
        v-for="entry in history.events"
        :key="entry.sequence"
        class="rounded-md border border-slate-200 bg-white p-4"
      >
        <p class="text-sm">
          <span class="font-mono text-xs">{{ entry.action }}</span>
          <template v-if="entry.transition">
            · {{ entry.transition.from }} → {{ entry.transition.to }}
          </template>
        </p>
        <p class="mt-1 text-xs text-slate-500">
          {{ entry.actor.display ?? entry.actor.kind }} · {{ entry.at }} · event {{ entry.sequence }}
        </p>
        <p
          v-if="entry.justification"
          class="mt-2 text-sm"
        >
          {{ entry.justification }}
        </p>
        <table
          v-if="(entry.diff ?? []).length > 0"
          class="mt-3 w-full text-left text-xs"
        >
          <thead class="text-slate-500">
            <tr>
              <th
                scope="col"
                class="py-1 font-medium"
              >
                Field
              </th>
              <th
                scope="col"
                class="py-1 font-medium"
              >
                Before
              </th>
              <th
                scope="col"
                class="py-1 font-medium"
              >
                After
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="change in entry.diff ?? []"
              :key="change.path"
            >
              <td class="py-1 font-mono">
                {{ change.path }}
              </td>
              <td class="py-1 font-mono">
                {{ show(change.before) }}
              </td>
              <td class="py-1 font-mono">
                {{ show(change.after) }}
              </td>
            </tr>
          </tbody>
        </table>
      </li>
    </ol>
  </section>
</template>
