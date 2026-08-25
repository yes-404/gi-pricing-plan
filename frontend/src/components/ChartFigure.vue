<script setup lang="ts">
/**
 * A chart and the table that says the same thing (NFR-OVR-10).
 *
 * WCAG 2.2 AA requires every chart to have an accessible tabular equivalent, and an ECharts
 * canvas offers a screen reader nothing at all. Two answers already exist in this repo and
 * neither is sufficient alone: `DoubleLiftChart.vue` encodes each series redundantly by line
 * type, which serves a reader who cannot distinguish hue but not one who cannot see the
 * canvas; `EbmShapePanel.vue` renders tables and no chart. This is the pairing, built once
 * here because W6b-1b adds nine charts and nine bespoke tables would diverge from each other
 * within a slice.
 *
 * The table is always in the DOM — never behind a disclosure and never `display: none`. A
 * `<details>` element would keep it out of the accessibility tree until opened, which is the
 * failure this component exists to avoid.
 */
defineProps<{
  /** Names the figure and labels the table. Two figures on a page must not share one. */
  title: string;
  /** Optional sentence under the heading — the place to say what a partition or a unit is. */
  caption?: string;
  columns: readonly string[];
  /** Row-major, one array per row, in the same order as `columns`. */
  rows: readonly (readonly (string | number | null)[])[];
}>();
</script>

<template>
  <figure class="mt-6">
    <figcaption>
      <h3 class="text-sm font-semibold text-slate-700">
        {{ title }}
      </h3>
      <p
        v-if="caption"
        class="mt-1 text-xs text-slate-500"
      >
        {{ caption }}
      </p>
    </figcaption>

    <slot />

    <table
      :aria-label="title"
      class="mt-2 w-full text-left text-sm"
    >
      <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
        <tr>
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
          v-for="(row, index) in rows"
          :key="index"
          class="border-b border-slate-100"
        >
          <td
            v-for="(cell, cellIndex) in row"
            :key="cellIndex"
            class="py-1 tabular-nums"
          >
            {{ cell ?? "—" }}
          </td>
        </tr>
      </tbody>
    </table>

    <p
      v-if="rows.length === 0"
      class="mt-1 text-xs text-slate-500"
    >
      No rows — this diagnostic recorded nothing for this model.
    </p>
  </figure>
</template>
