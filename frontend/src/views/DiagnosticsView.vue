<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { getDiagnostics, partitions, weightingLabel, type Diagnostics } from "@/api/diagnostics";
import { getModel, type Model } from "@/api/models";
import { ProblemError } from "@/api/problem";
import AeByFactorChart from "@/components/AeByFactorChart.vue";
import CalibrationChart from "@/components/CalibrationChart.vue";
import ComplexityTable from "@/components/ComplexityTable.vue";
import CrossValidationPanel from "@/components/CrossValidationPanel.vue";
import GbmEvalCurveChart from "@/components/GbmEvalCurveChart.vue";
import GbmImportanceCharts from "@/components/GbmImportanceCharts.vue";
import GlmDiagnosticsPanel from "@/components/GlmDiagnosticsPanel.vue";
import LiftChart from "@/components/LiftChart.vue";
import PartialDependencePanel from "@/components/PartialDependencePanel.vue";
import PartitionTable from "@/components/PartitionTable.vue";
import SurrogateNotice from "@/components/SurrogateNotice.vue";

const props = defineProps<{ slug: string; version?: string }>();

const diagnostics = ref<Diagnostics | null>(null);
const model = ref<Model | null>(null);
const loading = ref(true);
const problem = ref<ProblemError | null>(null);

const versionNumber = computed(() => (props.version ? Number(props.version) : undefined));

/**
 * The two partitions FR-MODEL-54 requires, and the only two the contract expresses.
 * `UniversalDiagnostics` declares `train` and `holdout` as separate `PartitionDiagnostics`;
 * `glm`, `complexity` and `cross_validation` declare neither, and `gbm` splits internally at
 * `GbmEvalPoint` rather than at member level. Nothing below this line may assume a partition
 * that its own field does not carry.
 */
const universal = computed(() =>
  diagnostics.value ? partitions(diagnostics.value.universal) : [],
);

const headline = computed(() => {
  const pair = universal.value;
  if (pair.length === 0) return [];
  const [train, holdout] = pair.map(([, partition]) => partition);
  if (!train || !holdout) return [];
  return [
    { name: "Rows", train: train.rows, holdout: holdout.rows },
    { name: "Overall A/E", train: train.ae_overall, holdout: holdout.ae_overall },
    { name: "Gini", train: train.gini, holdout: holdout.gini },
    { name: "Normalised Gini", train: train.gini_normalised, holdout: holdout.gini_normalised },
  ];
});

/**
 * The residual distribution per partition (FR-MODEL-50).
 *
 * All six fields `ResidualSummary` declares, not four. The plan's own list stopped at
 * mean/std/minimum/maximum; `diagnostics.py:124-134` also declares `p01` and `p99`, and
 * those two are the tails — the part of a residual distribution a reviewer reads first.
 * Dropping them would have shown a narrower distribution than the fit recorded.
 *
 * A table and not a chart: this artifact carries no per-row residual series to plot.
 */
const RESIDUAL_FIELDS = ["mean", "std", "minimum", "maximum", "p01", "p99"] as const;

const RESIDUAL_LABELS: Record<(typeof RESIDUAL_FIELDS)[number], string> = {
  mean: "Mean",
  std: "Std dev",
  minimum: "Minimum",
  maximum: "Maximum",
  p01: "P01",
  p99: "P99",
};

const residuals = computed(() => {
  const summaries = universal.value.map(([, partition]) => partition.residual_summary ?? null);
  if (summaries.every((summary) => summary === null)) return [];
  return RESIDUAL_FIELDS.map((field) => ({
    name: RESIDUAL_LABELS[field],
    values: summaries.map((summary) => summary?.[field] ?? null),
  }));
});

/**
 * FR-MODEL-55: the weighting is a property of each partition, and the two are the same
 * scheme on every fit this platform produces — but it is read off `train` rather than
 * assumed, and the holdout's is shown beside it when they differ, because a metric compared
 * across two weightings is not a comparison.
 */
const weighting = computed(() => {
  const [train, holdout] = universal.value.map(([, partition]) => partition);
  if (!train || !holdout) return null;
  return train.weighting === holdout.weighting
    ? weightingLabel(train.weighting)
    : `${weightingLabel(train.weighting)} on train, ${weightingLabel(holdout.weighting)} on holdout`;
});

/**
 * A surrogate's A/E denominator is another model's predictions (FR-MODEL-102). The flag
 * lives on the Model's spec, not on the diagnostics artifact, so this view fetches the model
 * as well — one extra read, against showing an A/E under a label that is wrong for it.
 */
const approximates = computed(() => {
  const spec = model.value?.spec ?? null;
  return spec?.model_type === "glm" ? (spec.approximates_model_id ?? null) : null;
});

onMounted(async () => {
  try {
    const [artifact, fetched] = await Promise.all([
      getDiagnostics(props.slug, versionNumber.value),
      getModel(props.slug, versionNumber.value),
    ]);
    diagnostics.value = artifact;
    model.value = fetched;
  } catch (error) {
    if (error instanceof ProblemError) problem.value = error;
    else throw error;
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <section>
    <header>
      <p class="text-xs uppercase tracking-wide text-slate-500">
        Diagnostics
      </p>
      <h1 class="mt-1 text-xl font-semibold tracking-tight">
        {{ slug }}
      </h1>
      <p
        v-if="diagnostics"
        class="mt-1 text-sm text-slate-500"
      >
        Computed at fit time and read since (FR-MODEL-49) — nothing on this page is
        recalculated.
        <span v-if="weighting"> Metrics are {{ weighting }}.</span>
      </p>
      <SurrogateNotice :approximates-model-id="approximates" />
    </header>

    <p
      v-if="loading"
      class="mt-6 text-sm text-slate-500"
    >
      Loading…
    </p>

    <p
      v-else-if="problem"
      class="mt-6 rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-900"
    >
      {{ problem.problem.detail ?? problem.problem.title }}
    </p>

    <template v-else-if="diagnostics">
      <section class="mt-8">
        <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Universal
        </h2>
        <table
          aria-label="Headline metrics"
          class="mt-2 w-full text-left text-sm"
        >
          <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th
                scope="col"
                class="py-2 font-medium"
              >
                Metric
              </th>
              <th
                v-for="[label] in universal"
                :key="label"
                scope="col"
                class="py-2 font-medium"
              >
                {{ label }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="metric in headline"
              :key="metric.name"
              class="border-b border-slate-100"
            >
              <th
                scope="row"
                class="py-1 font-normal"
              >
                {{ metric.name }}
              </th>
              <td class="py-1 tabular-nums">
                {{ metric.train }}
              </td>
              <td class="py-1 tabular-nums">
                {{ metric.holdout }}
              </td>
            </tr>
          </tbody>
        </table>

        <AeByFactorChart :partitions="universal" />
        <LiftChart :partitions="universal" />
        <CalibrationChart :partitions="universal" />

        <PartitionTable
          v-if="residuals.length"
          title="Residual summary"
          caption="Six summary statistics per partition. The per-row residual series is not carried by this artifact."
          :columns="universal.map(([label]) => label)"
          :rows="residuals"
        />
      </section>

      <section class="mt-8">
        <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Complexity
        </h2>
        <ComplexityTable :complexity="diagnostics.complexity" />
      </section>

      <!-- Guarded, not always mounted. `GlmDiagnostics` has no empty form, so a panel rendered
           for a model that has none would be a section of em dashes claiming a GLM was
           fitted — and in practice it throws before anything on the page renders at all. -->
      <section
        v-if="diagnostics.glm"
        class="mt-8"
      >
        <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
          GLM
        </h2>
        <GlmDiagnosticsPanel :glm="diagnostics.glm" />
      </section>

      <section
        v-if="diagnostics.gbm"
        class="mt-8"
      >
        <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
          GBM
        </h2>

        <GbmEvalCurveChart :eval-curve="diagnostics.gbm.eval_curve" />

        <GbmImportanceCharts
          :importances="diagnostics.gbm.importances"
          :permutation-importances="diagnostics.gbm.permutation_importances"
          :monotonicity="diagnostics.gbm.monotonicity"
        />

        <h3 class="mt-8 text-sm font-semibold text-slate-700">
          Partial dependence
        </h3>
        <PartialDependencePanel :partial-dependence="diagnostics.gbm.partial_dependence" />

        <table
          aria-label="Tree summary"
          class="mt-6 w-full text-left text-sm"
        >
          <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th
                scope="col"
                class="py-2 font-medium"
              >
                Measure
              </th>
              <th
                scope="col"
                class="py-2 font-medium"
              >
                Value
              </th>
            </tr>
          </thead>
          <tbody>
            <tr class="border-b border-slate-100">
              <th
                scope="row"
                class="py-1 font-normal"
              >
                Trees
              </th>
              <td class="py-1 tabular-nums">
                {{ diagnostics.gbm.tree_count }}
              </td>
            </tr>
            <tr class="border-b border-slate-100">
              <th
                scope="row"
                class="py-1 font-normal"
              >
                Max depth
              </th>
              <td class="py-1 tabular-nums">
                {{ diagnostics.gbm.max_depth }}
              </td>
            </tr>
            <tr class="border-b border-slate-100">
              <th
                scope="row"
                class="py-1 font-normal"
              >
                Mean depth
              </th>
              <td class="py-1 tabular-nums">
                {{ diagnostics.gbm.mean_depth }}
              </td>
            </tr>
          </tbody>
        </table>

        <!-- FR-MODEL-78. Present only on the second bound of a quantile pair, and a scalar
             record rather than a series: how often this model's prediction crossed its
             counterpart's, and by how much at worst. `QuantileBoundNotice` on the model page
             reads the spec's `interval_for` and says nothing about crossing; this is the
             measurement. Crossing is reported and never repaired (OQ-MODEL-2). -->
        <div
          v-if="diagnostics.gbm.quantile_crossing"
          class="mt-6 rounded-md border border-slate-200 bg-slate-50 p-4 text-sm"
        >
          <h3 class="font-semibold text-slate-700">
            Quantile crossing
          </h3>
          <p class="mt-1">
            {{ diagnostics.gbm.quantile_crossing.rows_crossing }} of
            {{ diagnostics.gbm.quantile_crossing.rows_checked }} checked rows crossed the
            counterpart bound, worst gap
            {{ diagnostics.gbm.quantile_crossing.worst_gap }}.
          </p>
          <p class="mt-1 text-xs text-slate-500">
            Counterpart model
            <span class="font-mono">{{
              diagnostics.gbm.quantile_crossing.counterpart_model_id
            }}</span>.
          </p>
        </div>
      </section>

      <!-- Populated only when the fit's `GlmSpec.select_by == "cv"`, so guarded: `None` here
           is the honest "this fit was not cross-validated" rather than an empty path standing
           in for one. -->
      <section
        v-if="diagnostics.cross_validation"
        class="mt-8"
      >
        <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Cross-validation
        </h2>
        <CrossValidationPanel :cross-validation="diagnostics.cross_validation" />
      </section>
    </template>
  </section>
</template>
