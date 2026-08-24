<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { getDiagnostics, partitions, weightingLabel, type Diagnostics } from "@/api/diagnostics";
import { getModel, type Model } from "@/api/models";
import { ProblemError } from "@/api/problem";
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
      </section>
    </template>
  </section>
</template>
