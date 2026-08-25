<script setup lang="ts">
import type { PartitionCaption } from "@/api/diagnostics";

/**
 * Scalar metrics with one column per partition (FR-MODEL-54).
 *
 * The partition columns are passed in rather than derived, so a caller cannot render a
 * holdout column for a diagnostic that has no holdout value — the misreading this slice
 * guards against. A caller with one partition passes one column.
 */
defineProps<{
  title: string;
  caption?: string;
  columns: readonly PartitionCaption[];
  rows: readonly { name: string; values: readonly (string | number | null)[] }[];
}>();
</script>

<template>
  <div class="mt-6">
    <p
      v-if="caption"
      class="text-xs text-slate-500"
    >
      {{ caption }}
    </p>
    <table
      :aria-label="title"
      class="mt-2 w-full text-left text-sm"
    >
      <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
        <tr>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Metric
          </th>
          <th
            v-for="column in columns"
            :key="column"
            scope="col"
            class="py-2 font-medium"
          >
            {{ column }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="row in rows"
          :key="row.name"
          class="border-b border-slate-100"
        >
          <th
            scope="row"
            class="py-1 font-normal"
          >
            {{ row.name }}
          </th>
          <td
            v-for="(value, index) in row.values"
            :key="index"
            class="py-1 tabular-nums"
          >
            {{ value ?? "—" }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
