<script setup lang="ts">
/**
 * FR-2143: the rows a figure leaves out because a factor that does not declare “map to base”
 * carries a level the fit has no relativity for, with their exposure, in three states: a count,
 * none left out, and not recorded (an artifact stored ahead of the rule). `null` is "not
 * recorded", `0` is "none": never one for the other. One component for the diagnostics, the
 * backtest and the comparison views, so the three say it the same way.
 */
export interface UnseenLevelNote {
  /** The partition the count belongs to: "Holdout", "Backtest", "Shared holdout". */
  label: string;
  rows: number | null;
  exposure: string | null;
}

defineProps<{
  notes: readonly UnseenLevelNote[];
  /** The sentence under the list: what happens to a quote with such a level, for this view. */
  note: string;
}>();
</script>

<template>
  <section
    aria-label="Rows on a level this fit never saw"
    class="mt-4 text-sm text-slate-700"
  >
    <h3 class="font-medium">
      Rows on a level this fit never saw
    </h3>
    <ul class="mt-1 space-y-1">
      <li
        v-for="entry in notes"
        :key="entry.label"
      >
        <template v-if="entry.rows === null">
          {{ entry.label }}: not recorded.
        </template>
        <template v-else-if="entry.rows === 0">
          {{ entry.label }}: none left out.
        </template>
        <template v-else>
          {{ entry.label }}: {{ entry.rows }} rows (exposure
          {{ entry.exposure ?? "not recorded" }}) are left out of every figure on this page.
        </template>
      </li>
    </ul>
    <p class="mt-1">
      {{ note }}
    </p>
  </section>
</template>
