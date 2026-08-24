<script setup lang="ts">
import { computed } from "vue";

import type { RelativityDifference } from "@/api/comparisons";
import ModelRefLink from "@/components/ModelRefLink.vue";

const props = defineProps<{
  differences: readonly RelativityDifference[];
  modelRefs: readonly string[];
}>();

/**
 * Grouped by factor, factors in the artifact's own order, levels within a factor ordered by
 * descending disagreement. The artifact imposes no order on the rows, and the row a selection
 * decision turns on is the level where the two models disagree most — so leaving them in
 * arrival order would bury it. A null difference sorts last: it means "not comparable", which
 * is weaker evidence than a difference of zero, not stronger.
 */
const groups = computed(() => {
  const byFactor = new Map<string, RelativityDifference[]>();
  for (const diff of props.differences) {
    const rows = byFactor.get(diff.factor);
    if (rows === undefined) byFactor.set(diff.factor, [diff]);
    else rows.push(diff);
  }
  return [...byFactor.entries()].map(([factor, rows]) => ({
    factor,
    rows: [...rows].sort((a, b) => (b.max_abs_difference ?? -1) - (a.max_abs_difference ?? -1)),
  }));
});

/**
 * The relativity for one model at this level, or `undefined` when the artifact does not carry
 * that model here at all — the same three-way reading as the metric table: em dash for "nobody
 * measured", `n/a` for a stored null meaning "does not apply".
 */
function valueFor(diff: RelativityDifference, modelRef: string): number | null | undefined {
  return diff.values.find((v) => v.model_ref === modelRef)?.value;
}

function format(value: number | null | undefined): string {
  if (value === undefined) return "—";
  if (value === null) return "n/a";
  return value.toFixed(4);
}
</script>

<template>
  <div>
    <section
      v-for="group in groups"
      :key="group.factor"
      class="mt-6"
    >
      <h3 class="font-mono text-sm font-medium text-slate-900">
        {{ group.factor }}
      </h3>
      <table
        class="mt-2 w-full text-left text-sm"
        :aria-label="`Relativity differences for ${group.factor}`"
      >
        <thead>
          <tr class="border-b border-slate-200">
            <th
              scope="col"
              class="py-2 font-medium"
            >
              Level
            </th>
            <th
              v-for="ref in props.modelRefs"
              :key="ref"
              scope="col"
              class="py-2 font-medium"
            >
              <ModelRefLink :model-ref="ref" />
            </th>
            <th
              scope="col"
              class="py-2 font-medium"
            >
              Max abs difference
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="diff in group.rows"
            :key="diff.level"
            class="border-b border-slate-100"
          >
            <th
              scope="row"
              class="py-2 font-mono text-xs font-normal"
            >
              {{ diff.level }}
            </th>
            <td
              v-for="ref in props.modelRefs"
              :key="ref"
              class="py-2 font-mono text-xs"
            >
              {{ format(valueFor(diff, ref)) }}
            </td>
            <td class="py-2 font-mono text-xs text-slate-600">
              {{ format(diff.max_abs_difference) }}
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>
