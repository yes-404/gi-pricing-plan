<script setup lang="ts">
/**
 * `02` §5.3's Custom metric library, `/metrics` (FR-167) — "the mirror of the objective
 * library above".
 *
 * **No link to a metric certificate.** The cell promises one and cites FR-162, which is
 * an API requirement carrying no link obligation, and §5.3 registers no metric-certificate
 * view to link to. Under FR-24 that cell binds nothing, so no link is owed. Building one
 * would build a view the specification has not declared.
 *
 * **Each certificate's provenance is shown below the table** (FR-2159): which certificate,
 * which Job produced it, and which metric version it certifies. Below and not in a row,
 * because the shared library table has no cell for it.
 */
import { onMounted, ref } from "vue";

import {
  getMetricCertificate,
  listMetrics,
  type CustomMetric,
  type MetricCertificate,
} from "@/api/metrics";
import { isProblem } from "@/api/problem";
import ArtifactLibraryTable, { type ArtifactRow } from "@/components/ArtifactLibraryTable.vue";
import ProvenanceBadge from "@/components/ProvenanceBadge.vue";

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

const certificates = ref<MetricCertificate[]>([]);
const certificateFailure = ref<string | undefined>(undefined);

/**
 * Only a metric whose `certificate_id` names a current certificate is asked, so only that
 * certificate's provenance shows. The fetch is the acceptance's item 2 on #1506; requesting it
 * only for a current certificate is slice 3's choice, not a recorded decision. A
 * re-certification that came back `failed` clears the pointer, so its certificate is not shown
 * here.
 *
 * A 404 `NOT_FOUND` (an unknown metric answers it too, e.g. one removed between the list and
 * the read) is "no certificate", not a failure: neither a badge nor an error.
 */
async function certificateOf(metric: CustomMetric): Promise<MetricCertificate | null> {
  if (!metric.certificate_id) return null;
  try {
    return await getMetricCertificate(metric.id);
  } catch (error) {
    if (isProblem(error, "NOT_FOUND")) return null;
    throw error;
  }
}

onMounted(async () => {
  let metrics: CustomMetric[];
  try {
    const list = await listMetrics();
    metrics = list.items;
    rows.value = metrics.map(toRow);
    truncated.value = list.truncated;
  } catch (error) {
    failure.value = error instanceof Error ? error.message : String(error);
    return;
  }
  // A failed certificate read takes down neither the library nor the other certificates'
  // badges: each read settles on its own, and a failure is said once beside what could be read.
  const settled = await Promise.allSettled(metrics.map(certificateOf));
  certificates.value = settled.flatMap((result) =>
    result.status === "fulfilled" && result.value !== null ? [result.value] : [],
  );
  const failed = settled.find((result) => result.status === "rejected");
  if (failed) {
    const reason = (failed as PromiseRejectedResult).reason;
    certificateFailure.value = reason instanceof Error ? reason.message : String(reason);
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

    <section
      v-if="!failure && certificates.length"
      class="mt-8"
    >
      <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
        Certificates
      </h2>
      <ProvenanceBadge
        v-for="certificate in certificates"
        :key="certificate.id"
        :provenance="certificate.provenance"
      />
    </section>
    <p
      v-if="certificateFailure"
      class="mt-4 text-sm text-rose-800"
    >
      The certificates could not be read: {{ certificateFailure }}
    </p>
  </section>
</template>
