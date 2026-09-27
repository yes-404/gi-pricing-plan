<script setup lang="ts">
/**
 * FR-135's ranked interaction candidates, each with FR-168's holdout strength
 * ratio — the panel whose owner clause this slice carries.
 *
 * **A suggestion is never an addition.** The platform never writes a Factor into a Model
 * Spec: an interaction becomes rateable only as an explicit `interaction` Factor carrying an
 * intent and a written rationale, named by the model document as an authored decision.
 * Auto-detected structure entering a rating basis unreviewed is the overfitting route
 * FR-135 refuses. So this panel offers a *starting point for authoring one*, and the
 * authoring is the actuary's.
 *
 * **No threshold, anywhere.** FR-168 is explicit that the ratio is ranked evidence and
 * never an admission test. There is no cutoff, no pass/fail styling and no "recommended"
 * marker — a colour that said "this one" would be a threshold wearing a different hat, and
 * FR-135's refusal to write a Factor would be undone by a UI that effectively did.
 *
 * **`1` is not the ratio's neutral point, and the panel must not imply it is.**
 * `OQ-608`: the published five are the top five *by in-sample strength* and the holdout
 * is a lookup on those five, so the denominator is a selected maximum while the numerator is
 * an independent re-measurement. The expected ratio sits below `1` even where the structure
 * is identical, and even at equal N. So the ratio is shown as a number beside its pair,
 * ordered by strength, and nothing here compares it to `1` or calls a value low.
 *
 * **An all-`null` set is ambiguous** (`OQ-612`): a pre-`W6b-5a` artifact carries no
 * ratio key at all and reaches the panel as `null`, exactly as a genuinely zero-strength
 * candidate does. The wording below is true of both, and the rebuild it offers is **not
 * promised to yield a value** — a genuine all-zero artifact recomputes to all-`null`.
 */
import { computed } from "vue";

import type { ShapSummary } from "@/api/models";

const props = defineProps<{
  summary: ShapSummary | null;
  /** So "no candidates" can be told from "this backend cannot find any". */
  interactionsAvailable: boolean;
}>();

const emit = defineEmits<{ author: [[string, string]] }>();

const candidates = computed(() => props.summary?.top_interactions ?? []);

/**
 * True when every candidate's ratio is absent — the one case `OQ-612` cannot resolve.
 *
 * A single `null` beside floats needs no such care: that pair had zero in-sample strength,
 * which is a finding and can be said plainly. It is *all* of them being absent that is
 * undecidable between "computed, nothing found" and "computed before the ratio existed".
 */
const ratiosUnavailable = computed(
  () =>
    candidates.value.length > 0
    && candidates.value.every((pair) => pair.holdout_strength_ratio == null),
);
</script>

<template>
  <section>
    <h2 class="mb-2 text-sm font-medium text-slate-700">
      Interaction candidates
    </h2>

    <p
      v-if="!interactionsAvailable"
      class="text-sm text-slate-500"
    >
      This model's backend does not compute interaction values, so there are no candidates
      to rank. That is a capability of the backend rather than a finding about the data.
    </p>

    <p
      v-else-if="!summary"
      class="text-sm text-slate-500"
    >
      This model has no SHAP summary.
    </p>

    <p
      v-else-if="!candidates.length"
      class="text-sm text-slate-500"
    >
      No interaction candidates were found.
    </p>

    <template v-else>
      <!--
        Ordered by in-sample strength, which is the order the artifact stores. Nothing here
        re-ranks by ratio: the ratio is evidence beside a candidate, not a competing score,
        and sorting by it would make it the admission test FR-168 forbids.
      -->
      <table class="w-full text-left text-sm">
        <caption class="sr-only">
          Interaction candidates ranked by SHAP interaction strength
        </caption>
        <thead class="border-b border-slate-200 text-xs uppercase text-slate-500">
          <tr>
            <th
              scope="col"
              class="py-1 font-medium"
            >
              Pair
            </th>
            <th
              scope="col"
              class="py-1 font-medium"
            >
              Strength
            </th>
            <th
              scope="col"
              class="py-1 font-medium"
            >
              Holdout ratio
            </th>
            <th
              scope="col"
              class="py-1 font-medium"
            >
              Author
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="pair in candidates"
            :key="pair.pair.join('|')"
            class="border-b border-slate-100"
          >
            <td class="py-1">
              {{ pair.pair[0] }} × {{ pair.pair[1] }}
            </td>
            <td class="py-1 tabular-nums">
              {{ pair.strength.toFixed(4) }}
            </td>
            <td class="py-1 tabular-nums">
              {{ pair.holdout_strength_ratio == null
                ? "—" : pair.holdout_strength_ratio.toFixed(2) }}
            </td>
            <td class="py-1">
              <button
                type="button"
                class="rounded-md border border-slate-300 px-2 py-0.5 text-xs"
                @click="emit('author', [pair.pair[0], pair.pair[1]])"
              >
                Author a factor
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <p
        v-if="ratiosUnavailable"
        class="mt-2 text-xs text-slate-500"
      >
        Holdout ratios are not available for this artifact. Rebuilding its transparency
        artifact will recompute them, though a model whose candidates carry no in-sample
        strength will still show none.
      </p>

      <p class="mt-2 text-xs text-slate-500">
        Ranked evidence, not a test. Adding an interaction is an authored decision: it
        becomes rateable only as an explicit factor carrying an intent and a rationale.
      </p>
    </template>
  </section>
</template>
