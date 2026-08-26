<script setup lang="ts">
import { onMounted, ref } from "vue";

import { listDatasets, type Dataset } from "@/api/datasets";
import { ProblemError } from "@/api/problem";
import StatusBadge from "@/components/StatusBadge.vue";

const datasets = ref<Dataset[]>([]);
const totalEstimate = ref(0);
const nextCursor = ref<string | null>(null);
const loading = ref(true);
const problem = ref<ProblemError | null>(null);

async function load(cursor?: string): Promise<void> {
  loading.value = true;
  problem.value = null;
  try {
    const page = await listDatasets({ cursor });
    datasets.value = cursor ? [...datasets.value, ...page.items] : page.items;
    nextCursor.value = page.next_cursor ?? null;
    totalEstimate.value = page.total_estimate;
  } catch (error) {
    if (error instanceof ProblemError) problem.value = error;
    else throw error;
  } finally {
    loading.value = false;
  }
}

/**
 * When this Dataset was last usable, and — only where it matters — which version that was.
 *
 * FR-DATA-50 scopes the badge and this date differently on purpose. The badge answers *what
 * state is the newest version in*; this answers *when was this Dataset last usable*, read off
 * "the most recently `validated` version, which **need not be the latest one**". A Dataset
 * whose v12 is a fresh `draft` above a `validated` v11 would otherwise render as never
 * validated.
 *
 * The requirement then adds the clause this function exists for: "**where the two refer to
 * different versions the list states which**, so the pair cannot be read as one fact." Named
 * only on disagreement, which is the requirement's own predicate — where they agree they *are*
 * one fact, and a version number in every row to disambiguate a case that is not present is
 * noise, not honesty.
 *
 * No branch handles a date without its version. `model_schema.datasets` raises when
 * `(last_validated_at is None) != (last_validated_version is None)` — "one fact (FR-DATA-50)"
 * — so the half-populated state cannot reach here, and a defensive branch would be dead code
 * asserting that a state exists which the contract forbids.
 */
function lastValidated(dataset: Dataset): string | null {
  if (dataset.last_validated_at == null) return null;

  const on = new Date(dataset.last_validated_at).toLocaleDateString();
  return dataset.last_validated_version === dataset.latest_version
    ? on
    : `v${dataset.last_validated_version} · ${on}`;
}

onMounted(() => void load());
</script>

<template>
  <section>
    <header class="mb-6 flex items-baseline justify-between">
      <h1 class="text-xl font-semibold tracking-tight">
        Datasets
      </h1>
      <!--
        `total_estimate` is capped, not exact (`00` §5.2) — an unbounded COUNT(*) over
        thirteen months of history is not worth one page header. Rendering it as "1,000+"
        past the cap is honest; rendering it as a total is not.
      -->
      <p
        v-if="!loading && !problem"
        class="text-sm text-slate-500"
      >
        {{ totalEstimate >= 1000 ? "1,000+" : totalEstimate }}
        {{ totalEstimate === 1 ? "dataset" : "datasets" }}
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
      <!-- The trace id is the whole point of showing an error at all: it turns "it broke"
           into something an operator can look up. -->
      <p
        v-if="problem.traceId"
        class="mt-2 font-mono text-xs text-red-700"
      >
        trace {{ problem.traceId }}
      </p>
    </div>

    <p
      v-else-if="datasets.length === 0"
      class="text-sm text-slate-500"
    >
      No datasets yet. Seed one with <code>examples/fremtpl2/seed.py</code>.
    </p>

    <table
      v-else
      class="w-full text-left text-sm"
    >
      <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
        <tr>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Name
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Line of business
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Territory
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Currency
          </th>
          <th
            scope="col"
            class="py-2 text-right font-medium"
          >
            Latest version
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Status
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Last validated
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Owner
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="dataset in datasets"
          :key="dataset.id"
          class="border-b border-slate-100"
        >
          <td class="py-3">
            <RouterLink
              :to="`/data/${dataset.slug}`"
              class="font-medium text-sky-700 hover:underline"
            >
              {{ dataset.name || dataset.slug }}
            </RouterLink>
            <span class="ml-2 font-mono text-xs text-slate-500">{{ dataset.slug }}</span>
          </td>
          <td class="py-3 text-slate-600">
            {{ dataset.line_of_business ?? "—" }}
          </td>
          <td class="py-3 text-slate-600">
            {{ dataset.territory ?? "—" }}
          </td>
          <td class="py-3 text-slate-600">
            {{ dataset.currency }}
          </td>
          <td class="py-3 text-right tabular-nums text-slate-600">
            {{ dataset.latest_version === null || dataset.latest_version === undefined
              ? "—" : `v${dataset.latest_version}` }}
          </td>
          <td class="py-3">
            <StatusBadge
              v-if="dataset.latest_version_status"
              :status="dataset.latest_version_status"
            />
            <span
              v-else
              class="text-slate-500"
            >—</span>
          </td>
          <td class="py-3 text-slate-600">
            {{ lastValidated(dataset) ?? "—" }}
          </td>
          <!--
            The whole `owner_id`, not a slice of it. An opaque id's only utility is exact copy
            and exact search, and `String.slice` destroys both; narrowing is presentational, so
            CSS does it. The value must also never live only in a `title`: a native tooltip is
            not dismissable, hoverable or persistent, and is unreachable by keyboard and touch
            — WCAG 2.2 SC 1.4.13, which NFR-OVR-10 binds this SPA to at AA.

            It names nobody, and that is the honest rendering: no endpoint resolves a principal
            id to a person (`/api/v1/me` answers for the caller alone), which is OQ-OVR-15.
          -->
          <td class="py-3">
            <span
              class="block max-w-[12ch] truncate font-mono text-xs text-slate-500"
            >{{ dataset.owner_id }}</span>
          </td>
        </tr>
      </tbody>
    </table>

    <button
      v-if="nextCursor"
      type="button"
      class="mt-4 rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-100"
      @click="load(nextCursor ?? undefined)"
    >
      Load more
    </button>
  </section>
</template>
