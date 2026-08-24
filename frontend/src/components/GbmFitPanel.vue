<script setup lang="ts">
import { computed } from "vue";

import type { GbmFitResult, GbmSpec } from "@/api/models";

const props = defineProps<{ spec: GbmSpec; fit: GbmFitResult }>();

/**
 * `monotone_constraints` is positional against `feature_order` (`02` §4.8). Zipping is what
 * turns a vector of integers into the actuarial judgement it encodes, and the words are the
 * accessible channel: a direction shown only as a coloured arrow is a direction a screen
 * reader does not have (NFR-OVR-10).
 */
const DIRECTION: Record<string, string> = {
  "-1": "decreasing",
  "0": "none",
  "1": "increasing",
};

const features = computed(() =>
  props.fit.feature_order.map((name, index) => ({
    name,
    dtype: props.fit.feature_dtypes?.[name] ?? "—",
    direction: DIRECTION[String(props.fit.monotone_constraints?.[index] ?? 0)] ?? "—",
    levels: Object.keys(props.fit.categorical_maps?.[name] ?? {}).length || null,
  })),
);

const objective = computed(() =>
  props.spec.objective.kind === "builtin" ? props.spec.objective.name : props.spec.objective.ref,
);

/**
 * FR-MODEL-94: the field names the transform the platform must apply, or is null where the
 * library already applied it. The value alone cannot distinguish those two readings, so the
 * page spells out which one holds rather than printing `exp` or a dash.
 */
const inverseLink = computed(() =>
  props.fit.inverse_link == null
    ? "The library has already applied it; the platform applies nothing further."
    : `The platform applies ${props.fit.inverse_link} to the raw score.`,
);

/**
 * FR-MODEL-27: exposure enters as a `base_margin` the platform constructs from the declared
 * offset — never as a feature and never as a weight. Which construction was used is the
 * difference between a frequency model and a nonsense one, so it is named rather than
 * summarised as "offset: yes".
 */
const baseMargin = computed(() => {
  const margin = props.fit.base_margin;
  if (margin.kind === "log_column") return `log(${margin.column})`;
  if (margin.kind === "column") return margin.column ?? "—";
  if (margin.kind === "model") return `model ${margin.offset_model_ref ?? "—"}`;
  return "none — every row carries the same exposure";
});

const libraries = computed(() =>
  Object.entries(props.fit.library_versions ?? {})
    .map(([name, version]) => `${name} ${version}`)
    .join(", "),
);
</script>

<template>
  <section class="mt-6">
    <h2 class="text-base font-semibold">
      The fitted booster
    </h2>

    <dl class="mt-3 grid grid-cols-2 gap-4 sm:grid-cols-4">
      <div class="rounded-md border border-slate-200 p-3">
        <dt class="text-xs uppercase tracking-wide text-slate-500">
          Rows fitted
        </dt>
        <dd class="mt-1 text-2xl font-semibold">
          {{ fit.rows.toLocaleString() }}
        </dd>
      </div>
      <div class="rounded-md border border-slate-200 p-3">
        <dt class="text-xs uppercase tracking-wide text-slate-500">
          Best iteration
        </dt>
        <dd class="mt-1 text-2xl font-semibold">
          {{ fit.best_iteration.toLocaleString() }}
        </dd>
      </div>
      <div class="rounded-md border border-slate-200 p-3">
        <dt class="text-xs uppercase tracking-wide text-slate-500">
          Features
        </dt>
        <dd class="mt-1 text-2xl font-semibold">
          {{ fit.feature_order.length }}
        </dd>
      </div>
      <div class="rounded-md border border-slate-200 p-3">
        <dt class="text-xs uppercase tracking-wide text-slate-500">
          Fit seconds
        </dt>
        <dd class="mt-1 text-2xl font-semibold">
          {{ fit.fit_seconds.toFixed(1) }}
        </dd>
      </div>
    </dl>

    <dl class="mt-4 space-y-2 text-sm">
      <div class="flex gap-2">
        <dt class="w-48 shrink-0 text-slate-500">
          Objective
        </dt>
        <dd class="font-mono text-xs">
          {{ objective }}
          <span class="font-sans text-slate-500">({{ spec.objective.kind }})</span>
        </dd>
      </div>
      <div class="flex gap-2">
        <dt class="w-48 shrink-0 text-slate-500">
          Base margin
        </dt>
        <!-- FR-MODEL-27: named, not summarised. "offset: yes" is not checkable. -->
        <dd class="font-mono text-xs">
          {{ baseMargin }}
        </dd>
      </div>
      <div class="flex gap-2">
        <dt class="w-48 shrink-0 text-slate-500">
          Inverse link
        </dt>
        <dd>{{ inverseLink }}</dd>
      </div>
      <div class="flex gap-2">
        <dt class="w-48 shrink-0 text-slate-500">
          Early stopping
        </dt>
        <dd v-if="spec.early_stopping">
          <span class="font-mono text-xs">{{ spec.early_stopping.metric }}</span>
          on {{ spec.early_stopping.on }}<template v-if="spec.early_stopping.cv_folds">
            ({{ spec.early_stopping.cv_folds }} folds)
          </template>, {{ spec.early_stopping.rounds }} rounds without improvement.
        </dd>
        <dd
          v-else
          class="text-slate-500"
        >
          None declared — the fit ran to its iteration limit.
        </dd>
      </div>
      <div class="flex gap-2">
        <dt class="w-48 shrink-0 text-slate-500">
          Booster
        </dt>
        <dd>
          {{ fit.booster_format }} ·
          <span class="font-mono text-xs">{{ fit.booster_blob.sha256.slice(0, 12) }}…</span>
          · {{ fit.booster_blob.bytes.toLocaleString() }} bytes
        </dd>
      </div>
      <div
        v-if="libraries"
        class="flex gap-2"
      >
        <dt class="w-48 shrink-0 text-slate-500">
          Fitted with
        </dt>
        <dd>{{ libraries }}</dd>
      </div>
    </dl>

    <!-- FR-MODEL-111: a declared metric the backend could not evaluate. Silent absence is
         the defect the field exists to remove, so this renders only when there is something
         to say and says "not evaluated" in words. -->
    <div
      v-if="fit.dropped_eval_metrics.length > 0"
      role="note"
      class="mt-4 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900"
    >
      <p class="font-medium">
        Declared eval metrics the backend could not evaluate
      </p>
      <ul class="mt-1 space-y-1">
        <li
          v-for="dropped in fit.dropped_eval_metrics"
          :key="dropped.name"
        >
          <span class="font-mono text-xs">{{ dropped.name }}</span> — not evaluated: the
          builtin was evaluated before the custom stopping metric, so the backend had no
          value for it.
        </li>
      </ul>
    </div>

    <table
      class="mt-6 w-full text-left text-sm"
      aria-label="Features and constraints"
    >
      <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
        <tr>
          <th class="py-2">
            Feature
          </th>
          <th class="py-2">
            Dtype
          </th>
          <th class="py-2">
            Monotone constraint
          </th>
          <th class="py-2">
            Levels
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="feature in features"
          :key="feature.name"
          class="border-b border-slate-100"
        >
          <td class="py-2 font-mono text-xs">
            {{ feature.name }}
          </td>
          <td class="py-2 font-mono text-xs text-slate-600">
            {{ feature.dtype }}
          </td>
          <!-- The word is the accessible channel, not a colour or an arrow (NFR-OVR-10). -->
          <td class="py-2">
            {{ feature.direction }}
          </td>
          <td class="py-2 text-slate-600">
            {{ feature.levels ?? "—" }}
          </td>
        </tr>
      </tbody>
    </table>

    <p class="mt-3 text-xs text-slate-500">
      Dtypes and categorical maps travel with the booster (FR-MODEL-31): the exported model
      cannot express them, so scoring elsewhere needs them from here.
    </p>
  </section>
</template>
