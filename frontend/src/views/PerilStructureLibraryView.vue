<script setup lang="ts">
/**
 * `02` §5.3's Peril structure library, `/peril-structures` (FR-MODEL-127).
 *
 * **Three columns, not five.** A Peril Structure has no `applicability` — FR-MODEL-44's
 * objective/metric concept — and FR-MODEL-127 gives it no usage count. Those columns are
 * declared absent rather than rendered blank: a blank cell would assert that a count exists
 * and is merely unknown.
 *
 * Each row links into the detail view, which is `:2595`'s own requirement and why this slice
 * cannot ship the library alone.
 */
import { onMounted, ref } from "vue";

import { listPerilStructures, type PerilStructure } from "@/api/perils";
import ArtifactLibraryTable, { type ArtifactRow } from "@/components/ArtifactLibraryTable.vue";

const PERIL_COLUMNS = ["slug", "version", "status"] as const;

const rows = ref<ArtifactRow[]>([]);
const truncated = ref(false);
const failure = ref<string | undefined>(undefined);

/**
 * `status` is optional in the contract with a default of `draft`, as on the other two
 * libraries. `applicability` and `usageCount` are deliberately not set at all — the column set
 * above is what decides they are not rendered, and giving them empty values here would make
 * the row claim a shape the artifact does not have.
 */
function toRow(structure: PerilStructure): ArtifactRow {
  return {
    id: structure.id,
    slug: structure.slug,
    version: structure.version,
    status: structure.status ?? "draft",
    href: `/peril-structures/${structure.id}`,
  };
}

onMounted(async () => {
  try {
    const list = await listPerilStructures();
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
      Peril structures
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
      :columns="PERIL_COLUMNS"
      :truncated="truncated"
      empty-label="No peril structures in this workspace yet."
    />
  </section>
</template>
