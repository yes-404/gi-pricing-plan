<script setup lang="ts">
import { computed } from "vue";

import type { EbmFitResult, EbmSpec, EbmTerm } from "@/api/models";

const props = defineProps<{ spec: EbmSpec; fit: EbmFitResult }>();

/**
 * The bin labels of one univariate term, in slot order and without slot 0.
 *
 * With `c` cuts the term carries `c + 3` slots — the unused base slot, `c + 1` populated
 * bins, and a trailing missing-value slot. A categorical feature with `L` levels carries
 * `L + 2`. Slot 0 is never reached by a lookup, so rendering it produces a bin with a 0.0
 * score that reads as a real level with no effect. An off-by-one here does not fail loudly;
 * it renders a shifted shape function that still looks like one.
 */
function labels(term: EbmTerm): string[] {
  const bins = props.fit.bins[term.term_features[0]!];
  if (bins === undefined) return [];
  if (bins.kind === "categorical") return [...bins.levels, "missing"];
  const cuts = bins.cuts;
  const inner = cuts.slice(0, -1).map((low, i) => `${low} – ${cuts[i + 1]}`);
  return [`< ${cuts[0]}`, ...inner, `≥ ${cuts[cuts.length - 1]}`, "missing"];
}

/**
 * A univariate term's slot vector. `scores`, `standard_deviations` and `bin_weights` are each
 * `number[]` for a univariate term and `number[][]` for a pair, and the narrowing is done by
 * inspecting the values rather than asserted, so a pair term reaching here yields nothing
 * instead of a row of `undefined`.
 */
function slots(vector: EbmTerm["scores"]): number[] {
  return vector.filter((value): value is number => typeof value === "number");
}

const univariate = computed(() =>
  props.fit.terms
    .filter((term) => term.term_features.length === 1)
    .map((term) => {
      const scores = slots(term.scores);
      const deviations = slots(term.standard_deviations);
      const weights = slots(term.bin_weights);
      return {
        name: term.term_name,
        rows: labels(term).map((label, i) => ({
          label,
          // Display index `i` is slot `i + 1`: slot 0 is dropped, not rendered.
          score: scores[i + 1] ?? 0,
          sd: deviations[i + 1] ?? 0,
          weight: weights[i + 1] ?? 0,
        })),
      };
    }),
);

/**
 * A pair term is a grid, and the only honest tabular rendering of a grid is a matrix that is
 * a heatmap in all but name — out of this slice's scope. Naming the term and saying why its
 * surface is absent is the alternative to silently dropping a term the fit contains.
 */
const interactions = computed(() =>
  props.fit.terms
    .filter((term) => term.term_features.length === 2)
    .map((term) => ({
      name: term.term_name,
      features: term.term_features.map((i) => props.fit.feature_order[i] ?? "?").join(" × "),
    })),
);
</script>

<template>
  <section class="mt-6">
    <h2 class="text-base font-semibold">
      Shape functions
    </h2>

    <dl class="mt-3 space-y-2 text-sm">
      <div class="flex gap-2">
        <dt class="w-48 shrink-0 text-slate-500">
          Intercept
        </dt>
        <!-- An EBM is additive on the response scale under the identity link: a score is an
             addition to the intercept, never a multiplier. Nothing in the numbers says which
             reading is meant, so the page says it. -->
        <dd class="font-mono text-xs">
          {{ fit.intercept.toFixed(4) }}
          <span class="font-sans text-slate-500">
            — scores add to this on the {{ fit.link }} link scale; they are not relativities.
          </span>
        </dd>
      </div>
      <div class="flex gap-2">
        <dt class="w-48 shrink-0 text-slate-500">
          Objective
        </dt>
        <dd class="font-mono text-xs">
          {{ fit.objective }}
        </dd>
      </div>
      <div class="flex gap-2">
        <dt class="w-48 shrink-0 text-slate-500">
          Binning and rounds
        </dt>
        <dd>
          up to {{ spec.max_bins }} bins, {{ spec.max_rounds?.toLocaleString() }} rounds;
          stopped at iteration {{ fit.best_iteration.toLocaleString() }}
        </dd>
      </div>
      <div class="flex gap-2">
        <dt class="w-48 shrink-0 text-slate-500">
          Interaction budget
        </dt>
        <dd>
          {{ spec.interactions ?? 0 }} pair term{{ (spec.interactions ?? 0) === 1 ? "" : "s" }}
        </dd>
      </div>
    </dl>

    <section
      v-for="term in univariate"
      :key="term.name"
      class="mt-6"
    >
      <h3 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
        {{ term.name }}
      </h3>
      <table
        :aria-label="`${term.name} shape function`"
        class="mt-2 w-full text-left text-sm"
      >
        <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th
              scope="col"
              class="py-2 font-medium"
            >
              Bin
            </th>
            <th
              scope="col"
              class="py-2 font-medium"
            >
              Score
            </th>
            <th
              scope="col"
              class="py-2 font-medium"
            >
              Std dev
            </th>
            <th
              scope="col"
              class="py-2 font-medium"
            >
              Weight
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in term.rows"
            :key="row.label"
            class="border-b border-slate-100"
          >
            <td class="py-2 font-mono text-xs">
              {{ row.label }}
            </td>
            <td class="py-2 font-mono text-xs">
              {{ row.score.toFixed(4) }}
            </td>
            <td class="py-2 font-mono text-xs text-slate-600">
              {{ row.sd.toFixed(4) }}
            </td>
            <!-- A zero weight is a bin no row landed in. Its 0.0 score is the absence of
                 evidence, not evidence of no effect, and the two are indistinguishable in
                 the number itself. -->
            <td class="py-2 font-mono text-xs text-slate-600">
              {{ row.weight.toLocaleString() }}
              <span
                v-if="row.weight === 0"
                class="ml-1 rounded bg-amber-100 px-1.5 py-0.5 font-sans text-amber-900"
              >unpopulated</span>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <section
      v-if="interactions.length > 0"
      class="mt-6"
    >
      <h3 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
        Interaction terms
      </h3>
      <ul class="mt-2 space-y-2 text-sm">
        <li
          v-for="term in interactions"
          :key="term.name"
        >
          <span class="font-mono text-xs">{{ term.name }}</span>
          <span class="text-slate-600">
            — a two-dimensional surface over {{ term.features }}, contributing to every
            prediction. It is named here rather than tabulated: the honest rendering of a
            grid is a chart, which this view does not yet have.
          </span>
        </li>
      </ul>
    </section>
  </section>
</template>
