<script setup lang="ts">
/**
 * `02` §5.3's Custom objective library, `/objectives` (FR-167): the list. Its editor, with
 * live parse errors, the derived gradient/hessian and the loss-curve preview, is
 * `ObjectiveEditorView` at `/objectives/new` (WK-690 Slice 5, FR-8140), linked from here.
 */
import { onMounted, ref } from "vue";

import { listObjectives, type CustomObjective } from "@/api/objectives";
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

/**
 * `status` carries a default of `draft` in the contract but is **not** in `required`, so it
 * reaches the client as possibly absent. Defaulted to the same value the contract defaults to
 * rather than widened in `ArtifactRow`: a row whose status is optional would make every badge
 * caller handle a case the platform does not produce.
 *
 * `applicability` *is* required, so it is read directly — an optional chain there would
 * suggest a state the contract forbids.
 */
function toRow(objective: CustomObjective): ArtifactRow {
  return {
    id: objective.id,
    slug: objective.slug,
    version: objective.version,
    status: objective.status ?? "draft",
    applicability: objective.applicability.responses,
    usageCount: objective.usage_count ?? 0,
    href: `/objectives/${objective.id}/certificate`,
  };
}

onMounted(async () => {
  try {
    const list = await listObjectives();
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
      Custom objectives
    </h1>
    <p class="mb-4 text-sm">
      <a
        href="/objectives/new"
        class="text-blue-700 underline"
      >New expression objective</a>
    </p>
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
      empty-label="No custom objectives in this workspace yet."
    />
  </section>
</template>
