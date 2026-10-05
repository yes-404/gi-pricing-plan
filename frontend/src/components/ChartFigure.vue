<script setup lang="ts" generic="T">
/**
 * A chart and a table that says at least what the chart says (NFR-463).
 *
 * The contract is a **superset**, not a transcription, and it was widened deliberately once
 * three charts had been wrapped. "The table that says the same thing" is the floor: every
 * plotted series must appear as a column. It is not the ceiling, because the canvas and the
 * table are read differently and a faithful transcription is not an equivalent one. A
 * sighted reader takes volume from the height of the exposure bars, so `DoubleLiftChart`
 * plots no row counts and its table carries them; a whisker on `OneWayChart` has no legend
 * entry and no tooltip, so the interval it draws is unreadable except as a column. Holding
 * callers to an exact transcription would have made both of those a violation.
 *
 * What the widening does not license is a table that omits a series, or one that shows a
 * *different* number from the one plotted. Both are what the tests here check.
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
 *
 * Each column is a descriptor, `{ key, label, value }`, and each cell is `column.value(row)`
 * over the caller's own row objects (RL-1307, OQ-550 (c)). The heading and the value's source
 * sit in one object, so a value cannot be placed under a heading it does not belong to
 * without the accessor itself being wrong, and `vue-tsc` checks every accessor against the
 * row type in the gate (`src/components/__typecheck__/`). The positional shape's two checks
 * went with it: the arity guard retired by construction, since every row now renders one
 * cell per column, and `cellUnder` (`src/test-tables.ts`) stays as the reader a test uses to
 * compare a table with its chart's data by label.
 */
import { computed } from "vue";

import type { Column } from "@/chart-table";

const props = defineProps<{
  /** Names the figure and labels the table. Two figures on a page must not share one. */
  title: string;
  /** Optional sentence under the heading: the place to say what a partition or a unit is. */
  caption?: string;
  /** One descriptor per column. The first column names each row, as its row header. */
  columns: readonly Column<T>[];
  /** The caller's own row objects. Each cell is read from one by its column's accessor. */
  rows: readonly T[];
}>();

/**
 * The refusal of two columns that share a `key`, in **every build** (RL-1307 item 5 (i)).
 *
 * `key` is the Vue key of every header and cell in its column, so two equal keys would let
 * Vue patch one column's cells with the other's: a table showing a value under a heading it
 * does not belong to, which is the violation this component exists to make impossible. A
 * label is display text and may repeat. There is deliberately no dev-only gate on this check.
 * RL-1307 retired the arity guard because it ran only in development, so this check runs in
 * production too. It does not throw, because a throw from a render blanks the page. The figure
 * shows a visible error in its table's place, and no table renders.
 */
const duplicateKeyError = computed<string | null>(() => {
  const seen = new Set<string>();
  for (const column of props.columns) {
    if (seen.has(column.key)) {
      return (
        `Table unavailable: two columns in "${props.title}" share the key "${column.key}" ` +
        `(${props.columns.map((c) => c.key).join(" | ")}).`
      );
    }
    seen.add(column.key);
  }
  return null;
});
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

    <p
      v-if="duplicateKeyError"
      role="alert"
      class="mt-2 text-sm text-red-700"
    >
      {{ duplicateKeyError }}
    </p>

    <table
      v-else
      :aria-label="title"
      class="mt-2 w-full text-left text-sm"
    >
      <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
        <tr>
          <th
            v-for="column in columns"
            :key="column.key"
            scope="col"
            class="py-2 font-medium"
          >
            {{ column.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(row, index) in rows"
          :key="index"
          class="border-b border-slate-100"
        >
          <template
            v-for="(column, columnIndex) in columns"
            :key="column.key"
          >
            <th
              v-if="columnIndex === 0"
              scope="row"
              class="py-1 font-normal tabular-nums"
            >
              {{ column.value(row) ?? "—" }}
            </th>
            <td
              v-else
              class="py-1 tabular-nums"
            >
              {{ column.value(row) ?? "—" }}
            </td>
          </template>
        </tr>
      </tbody>
    </table>

    <p
      v-if="!duplicateKeyError && rows.length === 0"
      class="mt-1 text-xs text-slate-500"
    >
      No rows — this figure has no data to show.
    </p>
  </figure>
</template>
