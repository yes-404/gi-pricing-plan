<script setup lang="ts">
/**
 * `02` §5.3's Custom metric library, `/metrics` (FR-167) — "the mirror of the objective
 * library above".
 *
 * **No link to a metric certificate.** The cell promises one and cites FR-162, which is
 * an API requirement carrying no link obligation, and §5.3 registers no metric-certificate
 * view to link to. Under FR-24 that cell binds nothing, so no link is owed. Building one
 * would build a view the specification has not declared.
 */
import { onMounted, ref } from "vue";

import { listMetrics, type CustomMetric } from "@/api/metrics";
import ArtifactLibraryTable, { type ArtifactRow } from "@/components/ArtifactLibraryTable.vue";

/**
 * The columns this library declares. Both objective and metric libraries have all five;
 * the peril-structure library declares three, because FR-167 gives a Peril Structure no
 * usage count and FR-153's applicability is not its concept.
 */
const LIBRARY_COLUMNS = ["slug", "version", "status", "applicability", "usageCount"] as const;


const rows = ref<ArtifactRow[]>([]);
const truncated = ref(false);
const failure = ref<string | undefined>(undefined);

/** Same defaulting as the objective library: `status` has a contract default but is optional. */
function toRow(metric: CustomMetric): ArtifactRow {
  return {
    id: metric.id,
    slug: metric.slug,
    version: metric.version,
    status: metric.status ?? "draft",
    applicability: metric.applicability.responses,
    usageCount: metric.usage_count ?? 0,
  };
}

onMounted(async () => {
  try {
    const list = await listMetrics();
    rows.value = list.items.map(toRow);
    truncated.value = list.truncated;
  } catch (error) {
    failure.value = error instanceof Error ? error.message : String(error);
  }
});
</script>

<template>
  <section class="p-6">
    <h1 class="mb-4 text-xl font-semibold">
      Custom metrics
    </h1>
    <p
      v-if="failure"
      class="text-sm text-rose-800"
    >
      {{ failure }}
    </p>
    <ArtifactLibraryTable
      v-else
      :rows="rows"
      :columns="LIBRARY_COLUMNS"
      :truncated="truncated"
      empty-label="No custom metrics in this workspace yet."
    />
  </section>
</template>
