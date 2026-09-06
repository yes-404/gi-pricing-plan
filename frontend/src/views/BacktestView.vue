<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { getBacktest, periodLabel, type Backtest } from "@/api/backtests";
import {
  weightingLabel,
  type PartitionCaption,
  type PartitionDiagnostics,
} from "@/api/diagnostics";
import { getModel, type Model } from "@/api/models";
import { ProblemError } from "@/api/problem";
import AeByFactorChart from "@/components/AeByFactorChart.vue";
import CalibrationChart from "@/components/CalibrationChart.vue";
import LiftChart from "@/components/LiftChart.vue";
import PartitionTable from "@/components/PartitionTable.vue";

const props = defineProps<{ slug: string; backtestId: string }>();

const backtest = ref<Backtest | null>(null);
const model = ref<Model | null>(null);
const loading = ref(true);
const problem = ref<ProblemError | null>(null);

/**
 * The backtest's one partition, in the shape the four shared instruments take.
 *
 * **Built here rather than through `partitions()`, deliberately.** That helper takes a
 * `UniversalDiagnostics` and a `BacktestSummary` has none. It exists to fix train-then-holdout
 * order across instruments, so that "a chart that plotted holdout first would compare against
 * the neighbouring chart wrongly" — a hazard between *two* partitions. At one element there is
 * no order to get wrong, and a one-partition helper would have no invariant to hold.
 *
 * **Revisit if a second single-partition caller appears**, because two of them would have to
 * agree on the caption vocabulary and that is an invariant worth a helper.
 *
 * The caption is `"Backtest"` and may not be the period or the `slug@version`: FR-187
 * forbids a caption that asserts a relationship the artifact does not carry, and the
 * instruments interpolate it straight into a heading (`${label} A/E`).
 */
const partition = computed<readonly (readonly [PartitionCaption, PartitionDiagnostics])[]>(() =>
  backtest.value === null ? [] : [["Backtest", backtest.value.summary.partition]],
);

const period = computed(() =>
  backtest.value === null ? null : periodLabel(backtest.value.summary),
);

const weighting = computed(() =>
  backtest.value === null ? null : weightingLabel(backtest.value.summary.partition.weighting),
);

/** FR-171's scalar metrics, one column because there is one partition. */
const headline = computed(() => {
  const found = backtest.value;
  if (found === null) return [];
  const p = found.summary.partition;
  return [
    { name: "Rows", values: [p.rows] },
    { name: "Overall A/E", values: [p.ae_overall] },
    { name: "Gini", values: [p.gini] },
    { name: "Normalised Gini", values: [p.gini_normalised] },
  ];
});

/**
 * All six fields `ResidualSummary` declares, not four — `p01` and `p99` are the tails, the
 * part of a residual distribution a reviewer reads first. `DiagnosticsView.vue` records the
 * same list and the same reason.
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
  // Optional *and* nullable in the contract, so a partition may carry none — and an absent
  // summary is an empty table rather than six blank rows. `DiagnosticsView.vue:73-80` drops
  // the table on the same condition, across both its partitions.
  const summary = backtest.value?.summary.partition.residual_summary ?? null;
  if (summary === null) return [];
  return RESIDUAL_FIELDS.map((field) => ({
    name: RESIDUAL_LABELS[field],
    values: [summary[field]],
  }));
});

onMounted(async () => {
  try {
    // The backtest is addressed by its own id (FR-94); the model is fetched only for
    // the breadcrumb and the link back to the fit, never to address the backtest.
    backtest.value = await getBacktest(props.backtestId);
    model.value = await getModel(props.slug);
  } catch (error) {
    if (error instanceof ProblemError) problem.value = error;
    else throw error;
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <main class="mx-auto max-w-5xl px-6 py-8">
    <header>
      <p class="text-xs uppercase tracking-wide text-slate-500">
        Backtest
      </p>
      <h1 class="mt-1 text-xl font-semibold tracking-tight">
        {{ slug }}
      </h1>
      <p
        v-if="backtest"
        class="mt-1 text-sm text-slate-500"
      >
        Measured against a version the model was not fitted on (FR-187).
        <span v-if="weighting"> Metrics are {{ weighting }}.</span>
      </p>
      <p
        v-if="model"
        class="mt-1 text-sm"
      >
        <RouterLink
          :to="{ name: 'model-detail', params: { slug } }"
          class="text-sky-700 underline"
        >
          Back to the fit
        </RouterLink>
      </p>
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

    <template v-else-if="backtest">
      <section class="mt-8">
        <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
          What was measured
        </h2>
        <dl class="mt-2 grid grid-cols-1 gap-x-6 gap-y-1 text-sm sm:grid-cols-2">
          <div>
            <dt class="inline text-slate-500">
              Model:
            </dt>
            <dd class="inline">
              {{ backtest.summary.model_ref }}
            </dd>
          </div>
          <div>
            <dt class="inline text-slate-500">
              Measured on:
            </dt>
            <dd class="inline">
              {{ backtest.summary.dataset_version_ref }}
            </dd>
          </div>
          <div>
            <dt class="inline text-slate-500">
              Fitted on:
            </dt>
            <dd class="inline">
              {{ backtest.summary.fitted_on_ref }}
            </dd>
          </div>
          <div>
            <dt class="inline text-slate-500">
              Period:
            </dt>
            <!--
              An artifact may declare no window: both fields are optional and nullable. That
              is an ordinary state and not an error, so it is said plainly rather than
              rendered as an empty date.
            -->
            <dd class="inline">
              {{ period ?? "No period declared" }}
            </dd>
          </div>
          <div>
            <dt class="inline text-slate-500">
              Computed at:
            </dt>
            <dd class="inline">
              {{ backtest.computed_at }}
            </dd>
          </div>
        </dl>
      </section>

      <section class="mt-8">
        <PartitionTable
          title="Headline metrics"
          :columns="['Backtest']"
          :rows="headline"
        />

        <AeByFactorChart :partitions="partition" />
        <LiftChart :partitions="partition" />
        <CalibrationChart :partitions="partition" />

        <PartitionTable
          v-if="residuals.length"
          title="Residual summary"
          caption="Six summary statistics. The per-row residual series is not carried by this artifact."
          :columns="['Backtest']"
          :rows="residuals"
        />
      </section>
    </template>
  </main>
</template>
