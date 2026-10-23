<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";

import { listEnvironments, ratingVersionRef, type Environment } from "@/api/environments";
import type { components } from "@/api/generated/schema";
import { ProblemError } from "@/api/problem";
import { listRatingVersions, type RatingVersion } from "@/api/ratingVersions";

type RatingVersionStatus = components["schemas"]["RatingVersionStatus"];

const STATUSES: RatingVersionStatus[] = ["draft", "review", "approved", "live", "retired"];

const versions = ref<RatingVersion[]>([]);
/** `null` = the live set was not read in full (403, a failed page, or the page cap): FR-8209. */
const environments = ref<Environment[] | null>(null);
const loading = ref(true);
const problem = ref<ProblemError | null>(null);
const statusFilter = ref<RatingVersionStatus | "all">("all");

/** Every page or nothing: a partial set of badges would read a live version as not live. */
async function readEnvironments(): Promise<Environment[] | null> {
  try {
    const { items, truncated } = await listEnvironments();
    return truncated ? null : items;
  } catch {
    return null;
  }
}

onMounted(async () => {
  try {
    [versions.value, environments.value] = await Promise.all([
      listRatingVersions(),
      readEnvironments(),
    ]);
  } catch (error) {
    if (error instanceof ProblemError) problem.value = error;
    else throw error;
  } finally {
    loading.value = false;
  }
});

/** Filtered by status and grouped by slug in the view; the route has no such parameters. */
const groups = computed(() => {
  const bySlug = new Map<string, RatingVersion[]>();
  for (const version of versions.value) {
    if (statusFilter.value !== "all" && version.status !== statusFilter.value) continue;
    bySlug.set(version.slug, [...(bySlug.get(version.slug) ?? []), version]);
  }
  const grouped = [...bySlug.entries()].map(([slug, rows]) => {
    const byVersion = [...rows].sort((a, b) => b.version - a.version);
    // DP-S10-4: a group sorts by its newest version's effective_from.
    const from = byVersion[0]?.effective_from;
    return { slug, rows: byVersion, from: from ? Date.parse(from) : null };
  });
  return grouped.sort((a, b) => {
    if (a.from !== b.from) {
      if (a.from === null) return 1;
      if (b.from === null) return -1;
      return b.from - a.from;
    }
    return a.slug.localeCompare(b.slug);
  });
});

/** The environments whose live set holds this version's `slug@version`: no join on `id`. */
function liveIn(version: RatingVersion): string[] {
  const ref_ = ratingVersionRef(version.slug, version.version);
  return (environments.value ?? [])
    .filter((env) => env.live_deployments.some((d) => d.rating_version_ref === ref_))
    .map((env) => env.slug);
}

/** `effective_from`/`effective_to` are business dates (FR-241): the date part, with no zone shift. */
function day(value: string | null | undefined): string {
  return value ? value.slice(0, 10) : "—";
}

/** The tables this version pins come with the list read, so no per-row lookup. */
function pinnedTables(version: RatingVersion) {
  return (version.pins?.rate_tables ?? []).flatMap((ref_) => {
    const match = /^rate_table:([^@]+)@(\d+)$/.exec(ref_);
    return match ? [{ slug: match[1]!, label: `${match[1]}@${match[2]}` }] : [];
  });
}

function base(version: RatingVersion): string {
  return `/rating/${version.slug}/v/${version.version}`;
}
</script>

<template>
  <section class="mx-auto max-w-5xl px-4 py-8">
    <h1 class="text-2xl font-semibold">
      Rating versions
    </h1>

    <p
      v-if="loading"
      class="mt-6 text-sm text-slate-500"
    >
      Loading…
    </p>

    <div
      v-else-if="problem"
      role="alert"
      class="mt-6 rounded-md border border-red-200 bg-red-50 p-4"
    >
      <p class="text-sm font-medium text-red-800">
        {{ problem.problem.title }}
      </p>
      <p class="mt-1 text-sm text-red-700">
        {{ problem.problem.detail }}
      </p>
    </div>

    <template v-else>
      <div class="mt-4 flex items-center gap-2 text-sm">
        <label
          for="status-filter"
          class="text-slate-500"
        >Status</label>
        <select
          id="status-filter"
          v-model="statusFilter"
          class="rounded-md border border-slate-300 px-2 py-1"
        >
          <option value="all">
            All
          </option>
          <option
            v-for="status in STATUSES"
            :key="status"
            :value="status"
          >
            {{ status }}
          </option>
        </select>
      </div>

      <p
        v-if="groups.length === 0"
        class="mt-6 text-sm text-slate-500"
      >
        No rating versions.
      </p>

      <section
        v-for="group in groups"
        :key="group.slug"
        class="mt-6"
      >
        <h2 class="text-lg font-medium">
          {{ group.slug }}
        </h2>
        <table class="mt-2 w-full text-left text-sm">
          <thead class="text-slate-500">
            <tr>
              <th scope="col">
                Version
              </th>
              <th scope="col">
                Status
              </th>
              <th scope="col">
                Live in
              </th>
              <th scope="col">
                Effective from
              </th>
              <th scope="col">
                Effective to
              </th>
              <th scope="col">
                Open
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="version in group.rows"
              :key="version.id"
              class="border-t border-slate-200 align-top"
            >
              <th
                scope="row"
                class="py-2 font-mono font-normal"
              >
                {{ version.slug }}@{{ version.version }}
              </th>
              <td>{{ version.status }}</td>
              <td>
                <span
                  v-if="environments === null"
                  class="text-slate-500"
                >unavailable</span>
                <span
                  v-for="env in liveIn(version)"
                  :key="env"
                  class="mr-1 rounded bg-emerald-100 px-1.5 py-0.5 text-emerald-800"
                >{{ env }}</span>
              </td>
              <td>{{ day(version.effective_from) }}</td>
              <td>{{ day(version.effective_to) }}</td>
              <td class="space-x-2">
                <RouterLink
                  :to="`${base(version)}/design`"
                  class="text-sky-700 underline"
                >
                  Design
                </RouterLink>
                <RouterLink
                  :to="`${base(version)}/sandbox`"
                  class="text-sky-700 underline"
                >
                  Sandbox
                </RouterLink>
                <RouterLink
                  :to="`${base(version)}/dislocation`"
                  class="text-sky-700 underline"
                >
                  Dislocation
                </RouterLink>
                <RouterLink
                  v-for="table in pinnedTables(version)"
                  :key="table.label"
                  :to="`${base(version)}/tables/${table.slug}`"
                  class="font-mono text-sky-700 underline"
                >
                  {{ table.label }}
                </RouterLink>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </template>
  </section>
</template>
