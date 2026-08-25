<script setup lang="ts">
/**
 * The list surface `02` §5.3 gives the objective and metric libraries — "the mirror of the
 * objective library above", built once and mounted twice (FR-MODEL-127).
 *
 * It takes rows, not artifacts: the two callers own the mapping from their own shape onto
 * this one, so this component never grows a branch on which library it is rendering.
 */
import ArtifactStatusBadge from "./ArtifactStatusBadge.vue";
import type { ObjectiveStatus } from "@/api/objectives";
import type { MetricStatus } from "@/api/metrics";

export interface ArtifactRow {
  id: string;
  slug: string;
  version: number;
  status: ObjectiveStatus | MetricStatus;
  applicability: string[];
  usageCount: number;
  href?: string;
}

defineProps<{ rows: ArtifactRow[]; truncated: boolean; emptyLabel: string }>();
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
          <th class="py-1">
            Slug
          </th>
          <th>Version</th>
          <th>Status</th>
          <th>Applicability</th>
          <th>Used by</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="row in rows"
          :key="row.id"
          class="border-t border-slate-200"
        >
          <td class="py-1">
            <RouterLink
              v-if="row.href"
              :to="row.href"
              class="text-sky-700 underline"
            >
              {{ row.slug }}
            </RouterLink>
            <span v-else>{{ row.slug }}</span>
          </td>
          <td>{{ row.version }}</td>
          <td><ArtifactStatusBadge :status="row.status" /></td>
          <td>{{ row.applicability.join(", ") || "—" }}</td>
          <td>{{ row.usageCount }}</td>
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
