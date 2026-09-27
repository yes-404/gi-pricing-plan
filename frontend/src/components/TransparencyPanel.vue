<script setup lang="ts">
import { computed } from "vue";

import type { TransparencyArtifact } from "@/api/models";

const props = defineProps<{
  artifact: TransparencyArtifact | null;
  state: "loading" | "ready" | "absent";
}>();

/**
 * FR-132's `monotonicity_verified` is boolean **or null**, and the third state is the one
 * that matters: null is "nobody ran the check". Collapsed into a two-state badge it becomes
 * either a pass or a failure, and both assert a result that does not exist.
 */
const monotonicity = computed(() => {
  const verified = props.artifact?.monotonicity_verified ?? null;
  if (verified === null) return "not assessed";
  return verified ? "verified" : "not verified";
});

const approximation = computed(() => props.artifact?.glm_approximation ?? null);
const shap = computed(() => props.artifact?.shap_summary ?? null);
const shapes = computed(() => props.artifact?.ebm_shape_functions ?? null);
</script>

<template>
  <section class="mt-8">
    <h2 class="text-base font-semibold">
      Transparency artifact
    </h2>

    <p
      v-if="state === 'loading'"
      class="mt-2 text-sm text-slate-500"
    >
      Loading…
    </p>

    <!-- FR-132 makes the artifact an obligation for a non-GLM Model, but not having one
         *yet* is a state rather than a failure. The red banner is for a call that went wrong;
         this is a model whose artifact has not been built. -->
    <p
      v-else-if="state === 'absent' || artifact === null"
      class="mt-2 rounded-md border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700"
    >
      No transparency artifact has been built for this model yet. FR-132 requires one
      before a non-GLM model can be used in a rating version; it is produced by a Job.
    </p>

    <template v-else>
      <!-- FR-133: the fidelity statement is where the approximation says where it stops
           being one. It goes first, in prose, because a reader who reads one thing here reads
           the first thing. -->
      <p class="mt-2 rounded-md border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
        {{ artifact.fidelity_statement }}
      </p>

      <dl class="mt-4 space-y-2 text-sm">
        <div class="flex gap-2">
          <dt class="w-48 shrink-0 text-slate-500">
            Monotonicity
          </dt>
          <dd>{{ monotonicity }}</dd>
        </div>
        <div class="flex gap-2">
          <dt class="w-48 shrink-0 text-slate-500">
            Built
          </dt>
          <dd>{{ artifact.created_at }}</dd>
        </div>
      </dl>

      <section
        v-if="approximation"
        class="mt-6"
      >
        <h3 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
          GLM approximation
        </h3>
        <dl class="mt-2 space-y-2 text-sm">
          <div class="flex gap-2">
            <dt class="w-48 shrink-0 text-slate-500">
              Fit to the booster
            </dt>
            <!-- Against `target`, not against observed claims: the approximation is fitted to
                 the source model's predictions, and an R² read as fit to experience is the
                 misreading FR-137 exists to prevent. -->
            <dd>
              R² {{ approximation.r_squared?.toFixed(3) }}, deviance explained
              {{ approximation.deviance_explained?.toFixed(3) }} — against
              <span class="font-mono text-xs">{{ approximation.target }}</span>, not against
              observed claims.
            </dd>
          </div>
          <div
            v-if="approximation.approximating_model_id"
            class="flex gap-2"
          >
            <dt class="w-48 shrink-0 text-slate-500">
              Approximating model
            </dt>
            <dd class="font-mono text-xs">
              {{ approximation.approximating_model_id }}
            </dd>
          </div>
        </dl>

        <table
          v-if="approximation.worst_regions?.length"
          aria-label="Where the approximation is worst"
          class="mt-3 w-full text-left text-sm"
        >
          <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th
                scope="col"
                class="py-2 font-medium"
              >
                Region
              </th>
              <th
                scope="col"
                class="py-2 font-medium"
              >
                Exposure
              </th>
              <th
                scope="col"
                class="py-2 font-medium"
              >
                Mean abs error
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="region in approximation.worst_regions"
              :key="region.description"
              class="border-b border-slate-100"
            >
              <td class="py-2">
                {{ region.description }}
              </td>
              <!-- The exposure share is what says whether a 11 % error is a rounding matter or
                   a book-sized one. The error without it is a number with no scale. -->
              <td class="py-2 font-mono text-xs">
                {{ (region.exposure_share * 100).toFixed(1) }} %
              </td>
              <td class="py-2 font-mono text-xs">
                {{ region.mean_abs_error_pct.toFixed(1) }} %
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <section
        v-if="shap"
        class="mt-6"
      >
        <h3 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
          SHAP summary
        </h3>
        <!-- A mean absolute contribution is a statistic of a sample. Without the sample size
             and the seed the ranking is one nobody can reproduce. `holdout_strength_ratio`
             (FR-168) has no column here: nothing publishes it yet, and an always-empty
             column reads as a computed zero. -->
        <p class="mt-1 text-xs text-slate-500">
          <span class="font-mono">{{ shap.algorithm }}</span> over
          {{ shap.sample_rows?.toLocaleString() }} sampled rows, seed {{ shap.seed }}.
          <template v-if="!shap.interactions_available">
            Interaction values were not computed for this summary.
          </template>
        </p>

        <table
          v-if="shap.mean_abs_contribution?.length"
          aria-label="Mean absolute SHAP contribution"
          class="mt-3 w-full text-left text-sm"
        >
          <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th
                scope="col"
                class="py-2 font-medium"
              >
                Factor
              </th>
              <th
                scope="col"
                class="py-2 font-medium"
              >
                Mean |contribution|
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in shap.mean_abs_contribution"
              :key="row.factor"
              class="border-b border-slate-100"
            >
              <td class="py-2 font-mono text-xs">
                {{ row.factor }}
              </td>
              <td class="py-2 font-mono text-xs">
                {{ row.value.toFixed(4) }}
              </td>
            </tr>
          </tbody>
        </table>

        <ul
          v-if="shap.top_interactions?.length"
          class="mt-3 space-y-1 text-sm"
        >
          <li
            v-for="pair in shap.top_interactions"
            :key="pair.pair.join('×')"
          >
            <span class="font-mono text-xs">{{ pair.pair.join(" × ") }}</span>
            <span class="text-slate-600"> — strength {{ pair.strength.toFixed(4) }}</span>
          </li>
        </ul>
      </section>

      <p
        v-if="shapes"
        class="mt-6 text-sm text-slate-600"
      >
        Shape functions for this model are stored as a blob
        (<span class="font-mono text-xs">{{ shapes.terms_blob }}</span>) rather than inline.
      </p>
    </template>
  </section>
</template>
