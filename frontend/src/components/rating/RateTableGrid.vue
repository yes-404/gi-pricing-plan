<script setup lang="ts">
/**
 * A Rate Table Version's cells as a typed grid (FR-228): the declared key columns in order,
 * then the value column with its unit. Columns are data, so they are built from the
 * definition. Paging is the server's cursor (FR-232), so the table is core-only: no
 * pagination, sorting or filtering feature, and `rows` is exactly the page shown.
 */
import { FlexRender, tableFeatures, useTable } from "@tanstack/vue-table";
import { computed } from "vue";

import type { RateTable, RateTableCell } from "@/api/rateTables";

import DecimalCellInput from "./DecimalCellInput.vue";

const props = defineProps<{
  table: RateTable;
  rows: RateTableCell[];
  /** Typed values by row key, over the stored ones. */
  edits: Record<string, string>;
  /** The server's error by row key (FR-234). */
  errors: Record<string, string>;
}>();
const emit = defineEmits<{ edit: [key: string, value: string] }>();

const SEPARATOR = "\u001f";
const features = tableFeatures({});
const keyNames = computed(() => props.table.keys.map((key) => key.name));
const valueName = computed(() => props.table.value.name);
const integerValue = computed(
  () => props.table.value.type === "money_minor" || props.table.value.type === "count",
);

function rowKey(row: RateTableCell): string {
  return keyNames.value.map((name) => row[name]).join(SEPARATOR);
}

const columns = computed(() => [
  ...keyNames.value.map((name) => ({
    id: name,
    header: name,
    accessorFn: (row: RateTableCell) => row[name] ?? "",
  })),
  {
    id: "value",
    header: `${props.table.value.name} (${props.table.value.unit})`,
    accessorFn: (row: RateTableCell) => row[props.table.value.name] ?? "",
  },
]);
const data = computed(() => props.rows);
const grid = useTable({ features, columns, data, getRowId: (row: RateTableCell) => rowKey(row) });

function shown(row: RateTableCell): string {
  return props.edits[rowKey(row)] ?? row[valueName.value] ?? "";
}
</script>

<template>
  <table class="min-w-full border-collapse text-sm">
    <thead>
      <tr
        v-for="group in grid.getHeaderGroups()"
        :key="group.id"
      >
        <th
          v-for="header in group.headers"
          :key="header.id"
          scope="col"
          class="border-b border-slate-300 px-3 py-2 text-left font-semibold"
        >
          <FlexRender :header="header" />
        </th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="row in grid.getRowModel().rows"
        :key="row.id"
      >
        <th
          v-for="name in keyNames"
          :key="name"
          scope="row"
          class="border-b border-slate-100 px-3 py-1 text-left font-normal"
        >
          {{ row.original[name] }}
        </th>
        <td class="border-b border-slate-100 px-3 py-1">
          <DecimalCellInput
            :model-value="shown(row.original)"
            :invalid="errors[row.id]"
            :integer="integerValue"
            :label="`${valueName} for ${keyNames.map((n) => `${n} ${row.original[n]}`).join(', ')}`"
            @update:model-value="emit('edit', row.id, $event)"
          />
        </td>
      </tr>
    </tbody>
  </table>
</template>
