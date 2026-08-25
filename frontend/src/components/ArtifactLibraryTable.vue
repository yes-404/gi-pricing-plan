<script setup lang="ts">
/**
 * The list surface `02` §5.3 gives the objective, metric and peril-structure libraries — built
 * once and mounted three times (FR-MODEL-127).
 *
 * It takes rows, not artifacts: the callers own the mapping from their own shape onto this
 * one, so this component never grows a branch on which library it is rendering.
 *
 * **Rendering is driven by `columns`, never by whether a row's value is present.** A Peril
 * Structure has no `applicability` — that is FR-MODEL-44's objective/metric concept — and
 * FR-MODEL-127 forbids it a usage count outright. Rendering those as blank cells would be
 * worse than wrong: **a blank cell is indistinguishable from a zero, a null and a failed
 * fetch**, so an empty usage cell asserts that a count exists and happens to be unknown, which
 * is the opposite of what the requirement says. The column is *absent*, and the test asserts
 * the header is not rendered rather than that the cell is empty.
 */
import ArtifactStatusBadge from "./ArtifactStatusBadge.vue";
import type { ObjectiveStatus } from "@/api/objectives";
import type { MetricStatus } from "@/api/metrics";
import type { PerilStructureStatus } from "@/api/perils";

export type ArtifactColumn = "slug" | "version" | "status" | "applicability" | "usageCount";

export interface ArtifactRow {
  id: string;
  slug: string;
  version: number;
  status: ObjectiveStatus | MetricStatus | PerilStructureStatus;
  /** Objectives and metrics only — FR-MODEL-44's concept, which a Peril Structure lacks. */
  applicability?: string[];
  /** Objectives and metrics only — FR-MODEL-127 forbids a Peril Structure one. */
  usageCount?: number;
  href?: string;
}

defineProps<{
  rows: ArtifactRow[];
  columns: readonly ArtifactColumn[];
  truncated: boolean;
  emptyLabel: string;
}>();

const HEADING: Record<ArtifactColumn, string> = {
  slug: "Slug",
  version: "Version",
  status: "Status",
  applicability: "Applicability",
  usageCount: "Used by",
};
</script>

<template>
  <div>
    <p
      v-if="truncated"
      class="mb-2 rounded bg-amber-50 px-3 py-2 text-sm text-amber-900"
    >
      Showing the first {{ rows.length }}. More exist than this page swept — narrow by status to
      see them.
    </p>

    <table
      v-if="rows.length"
      class="w-full text-sm"
    >
      <thead>
        <tr class="text-left text-slate-500">
          <th
            v-for="column in columns"
            :key="column"
            class="py-1"
          >
            {{ HEADING[column] }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="row in rows"
          :key="row.id"
          class="border-t border-slate-200"
        >
          <!-- One cell per declared column, so no row can be ragged and no column can appear
               for one row and not another. -->
          <td
            v-for="column in columns"
            :key="column"
            class="py-1"
          >
            <template v-if="column === 'slug'">
              <RouterLink
                v-if="row.href"
                :to="row.href"
                class="text-sky-700 underline"
              >
                {{ row.slug }}
              </RouterLink>
              <span v-else>{{ row.slug }}</span>
            </template>
            <template v-else-if="column === 'version'">
              {{ row.version }}
            </template>
            <ArtifactStatusBadge
              v-else-if="column === 'status'"
              :status="row.status"
            />
            <template v-else-if="column === 'applicability'">
              {{ (row.applicability ?? []).join(", ") || "—" }}
            </template>
            <template v-else>
              {{ row.usageCount ?? "—" }}
            </template>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Only when the sweep was complete. An empty page under a truncated sweep is not an
         empty library, and saying so is a claim this component cannot support. -->
    <p
      v-else-if="!truncated"
      class="text-sm text-slate-500"
    >
      {{ emptyLabel }}
    </p>
  </div>
</template>
