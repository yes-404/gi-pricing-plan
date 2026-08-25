<script setup lang="ts">
import { computed } from "vue";

import { psiBand, type ColumnComparison } from "@/api/profiles";

/**
 * One column's drift against a reference version (FR-DATA-28).
 *
 * `drift` carries three states, not two. `undefined` means no comparison has been loaded;
 * `null` means one has, and this column is **not in it** — `compare_profiles` skips a
 * column the reference profile does not have, so its absence says the column is new rather
 * than that it did not move.
 */
const props = defineProps<{
  drift: ColumnComparison | null | undefined;
  /**
   * The banding threshold: VR-DST-1's `warn_above`, as the workspace's approved version
   * of the rule states it — or `null` when no such rule is known (in flight, or absent
   * from the workspace). `null` renders "unbanded": the screen must not invent the 0.1
   * the rule owns, because a screen-side literal was exactly the disagreement with the
   * report this prop removes.
   */
  warnAbove: number | null;
}>();

/**
 * The band, or `null` when there is nothing to band.
 *
 * `psi` is null for any column whose `top_levels` carry no non-null level — every
 * continuous column in practice. `psiBand` refuses that argument outright, and this guard
 * is why: an unmeasured PSI must render as absent, never as the calm end of a scale
 * nobody computed. `warnAbove` null is the other refusal — a measured PSI with no rule to
 * band it against is "unbanded", and falling back to a literal here would restore the
 * number `W6b-13` removed.
 */
const band = computed(() => {
  if (props.drift?.psi == null || props.warnAbove == null) return null;
  return psiBand(props.drift.psi, props.warnAbove);
});

const TONE = {
  stable: "text-emerald-700",
  shifted: "text-amber-700",
} as const;
</script>

<template>
  <p
    v-if="drift === null"
    class="mt-2 text-xs font-medium text-sky-700"
  >
    new in this version
  </p>
  <dl
    v-else-if="drift"
    class="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-xs tabular-nums"
  >
    <div>
      <dt class="sr-only">
        PSI
      </dt>
      <dd
        v-if="band"
        :class="['font-medium', TONE[band]]"
      >
        PSI {{ drift.psi?.toFixed(3) }}
      </dd>
      <!-- Uncoloured on purpose: there is a measurement but no rule to band it against
           (VR-DST-1 not yet loaded, or absent from this workspace). "Unbanded" is a
           statement — the alternative is inventing a threshold, which is how the screen
           used to disagree with the report. -->
      <dd
        v-else-if="drift.psi != null"
        class="text-slate-500"
      >
        PSI {{ drift.psi.toFixed(3) }} unbanded
      </dd>
      <!-- Uncoloured on purpose: there is no band, because there was no measurement. -->
      <dd
        v-else
        class="text-slate-500"
      >
        PSI not measured
      </dd>
    </div>
    <div v-if="drift.mean_shift != null && drift.mean_shift !== 0">
      <dt class="sr-only">
        Mean shift
      </dt>
      <!-- An absolute difference in the column's own units: `current.mean − reference.mean`,
           not a ratio and not a percentage. -->
      <dd class="text-slate-600">
        {{ drift.mean_shift > 0 ? "+" : "" }}{{ drift.mean_shift.toFixed(3) }} mean
      </dd>
    </div>
    <div v-if="drift.null_rate_shift">
      <dt class="sr-only">
        Null-rate shift
      </dt>
      <!-- Percentage **points**: a null rate moving 0.010 → 0.022 is +1.20pp. Rendering it
           as a percentage would read as a relative change and overstate a small book. -->
      <dd class="text-slate-600">
        {{ drift.null_rate_shift > 0 ? "+" : "" }}{{ (drift.null_rate_shift * 100).toFixed(2) }}pp nulls
      </dd>
    </div>
    <div v-if="drift.new_levels.length">
      <dt class="sr-only">
        New levels
      </dt>
      <dd
        class="text-slate-600"
        :title="drift.new_levels.join(', ')"
      >
        +{{ drift.new_levels.length }} new
      </dd>
    </div>
    <div v-if="drift.vanished_levels.length">
      <dt class="sr-only">
        Vanished levels
      </dt>
      <dd
        class="text-slate-600"
        :title="drift.vanished_levels.join(', ')"
      >
        {{ drift.vanished_levels.length }} vanished
      </dd>
    </div>
  </dl>
</template>
