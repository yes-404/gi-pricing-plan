<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import {
  getDiagnostics,
  partitions,
  weightingLabel,
  type AeCell,
  type Diagnostics,
  type FactorFinerLevels,
  type FinerLevelAe,
  type PartitionLabel,
} from "@/api/diagnostics";
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
import ProvenanceBadge from "@/components/ProvenanceBadge.vue";
import SurrogateNotice from "@/components/SurrogateNotice.vue";

const props = defineProps<{ slug: string; version?: string }>();

const diagnostics = ref<Diagnostics | null>(null);
const model = ref<Model | null>(null);
const loading = ref(true);
const problem = ref<ProblemError | null>(null);

const versionNumber = computed(() => (props.version ? Number(props.version) : undefined));

/**
 * The two partitions FR-183 requires, and the only two the contract expresses.
 * `UniversalDiagnostics` declares `train` and `holdout` as separate `PartitionDiagnostics`;
 * `glm`, `complexity` and `cross_validation` declare neither, and `gbm` splits internally at
 * `GbmEvalPoint` rather than at member level. Nothing below this line may assume a partition
 * that its own field does not carry.
 */
const universal = computed(() =>
  diagnostics.value ? partitions(diagnostics.value.universal) : [],
);

/**
 * FR-2143: rows left out of a partition because a factor that does not declare “map to base”
 * carries a level the fit has no relativity for. `null` is "not recorded" (a fit stored ahead of
 * the rule), `0` is "none": never one for the other. A GLM's fit only: a GBM or an EBM refuses
 * such a level whatever is declared, and its diagnostics never record these counts.
 */
const unseenRows = computed(() =>
  universal.value.map(([label, partition]) => {
    const rows = partition.rows_excluded_unseen_level ?? null;
    const exposure = partition.exposure_excluded_unseen_level ?? null;
    return { label, rows, exposure };
  }),
);

/**
 * FR-109's finer level (`02` §5.3, "Diagnostics, finer level"; decision #1870 (b)). The fit
 * stored it once, as `Diagnostics.finer_level_ae` with train and holdout, and this view only
 * selects among what was stored; nothing is computed here (FR-170). Three states, the
 * maintainer's (c) on #1506:
 *
 * - no Factor on a chained grouping: no finer-level section at all, whenever the model was
 *   fitted. A `null` field cannot say this by itself, so the read carries `chained_factors`,
 *   which the API composes from the model's definition by the fit's own rule (`02` §5.1;
 *   decided on #1961, comment 7060609084, point 1). The view applies no rule of its own.
 * - such a Factor, and `finer_level_ae` `null` or absent: fitted before the finer level was
 *   stored. The view says "not available", in those words, names the Factors, and shows no
 *   table.
 * - such a Factor, fitted after: a level selector and the tables for that Factor.
 *
 * A surrogate's finer level is read under the page's `SurrogateNotice` (FR-141), as its other
 * actual-versus-expected tables are: its "actual" is the source model's prediction.
 *
 * The artifact holds train and holdout to the same Factors and levels (FR-183), so the Factors
 * are read off the holdout and each table is drawn for both partitions side by side.
 */
const finer = computed(() => diagnostics.value?.finer_level_ae ?? null);

const finerAvailable = computed(() => finer.value !== null);

/** The model's Factors on a chained grouping, as the read names them (`chained_factors`). */
const chainedSlugs = computed<string[]>(() => [...(diagnostics.value?.chained_factors ?? [])]);

/** "Not available": a Factor that has a finer level, and none stored for it. */
const finerNotAvailable = computed(() => !finerAvailable.value && chainedSlugs.value.length > 0);

const chainedFactors = computed<FactorFinerLevels[]>(() => finer.value?.holdout ?? []);

function finerOf(label: PartitionLabel): FactorFinerLevels[] {
  return (label === "Train" ? finer.value?.train : finer.value?.holdout) ?? [];
}

/** The selected level per Factor; `""` is the level the model was fitted on. */
const selectedLevel = ref<Record<string, string>>({});

/**
 * Whether the fit stored the Factor's own A/E. An interaction's operand is not a term of the
 * model (`resolve_factors`), so it has finer levels but no "as fitted" table; for it the view
 * offers only the finer levels and opens on the finest, never an empty table.
 */
function hasFitted(entry: FactorFinerLevels): boolean {
  return universal.value.some(([, partition]) =>
    (partition.ae_by_factor ?? []).some((cell) => cell.factor === entry.factor),
  );
}

/** The level shown for `entry`: the one chosen, else as fitted, else the finest stored. */
function selectedOf(entry: FactorFinerLevels): string {
  return (
    selectedLevel.value[entry.factor] ??
    (hasFitted(entry) ? "" : (entry.levels[0]?.name ?? ""))
  );
}

function choose(factor: string, event: Event): void {
  selectedLevel.value = {
    ...selectedLevel.value,
    [factor]: (event.target as HTMLSelectElement).value,
  };
}

interface FinerRow {
  level: string;
  ae: number | null;
  actual: number;
  expected: number;
  exposure: string | null;
}

interface FinerTable {
  label: PartitionLabel;
  rows: FinerRow[];
  /** The named "not available" row of a finer level; `null` for the fitted level. */
  unavailable: { rows: number; exposure: string; actual: number; expected: number } | null;
}

function cellRow(cell: AeCell): FinerRow {
  return {
    level: cell.level,
    ae: cell.ae,
    actual: cell.actual,
    expected: cell.expected,
    exposure: cell.exposure_years ?? null,
  };
}

function finerTables(entry: FactorFinerLevels): FinerTable[] {
  const name = selectedOf(entry);
  return universal.value.map(([label, partition]) => {
    if (name === "") {
      // The fitted level: the Factor's own A/E, as `ae_by_factor` stored it.
      const cells = partition.ae_by_factor?.filter((cell) => cell.factor === entry.factor) ?? [];
      return { label, rows: cells.map(cellRow), unavailable: null };
    }
    const own = finerOf(label).find((item) => item.factor === entry.factor);
    const level: FinerLevelAe | undefined = own?.levels.find((item) => item.name === name);
    return {
      label,
      rows: (level?.cells ?? []).map(cellRow),
      unavailable: level
        ? {
            rows: level.unavailable_rows,
            exposure: level.unavailable_exposure,
            actual: level.unavailable_actual,
            expected: level.unavailable_expected,
          }
        : null,
    };
  });
}

function levelCaption(entry: FactorFinerLevels): string {
  const name = selectedOf(entry);
  return name === "" ? `${entry.grouping} (as fitted)` : name;
}

function figure(value: number | null): string {
  return value === null ? "—" : String(Number(value.toPrecision(4)));
}

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
 * The residual distribution per partition (FR-171).
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
 * FR-184: the weighting is a property of each partition, and the two are the same
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
 * A surrogate's A/E denominator is another model's predictions (FR-141). The flag
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
        Computed at fit time and read since (FR-170) — nothing on this page is
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
      <ProvenanceBadge :provenance="diagnostics.provenance" />

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

        <section
          v-if="diagnostics.glm"
          aria-label="Rows on a level this fit never saw"
          class="mt-4 text-sm text-slate-700"
        >
          <h3 class="font-medium">
            Rows on a level this fit never saw
          </h3>
          <ul class="mt-1 space-y-1">
            <li
              v-for="note in unseenRows"
              :key="note.label"
            >
              <template v-if="note.rows === null">
                {{ note.label }}: not recorded.
              </template>
              <template v-else-if="note.rows === 0">
                {{ note.label }}: none left out.
              </template>
              <template v-else>
                {{ note.label }}: {{ note.rows }} rows (exposure {{ note.exposure }}) are left out of
                every figure on this page.
              </template>
            </li>
          </ul>
          <p class="mt-1">
            A quote with such a level is refused, unless the factor declares “map to base”.
          </p>
        </section>

        <AeByFactorChart :partitions="universal" />

        <!-- FR-109's finer level (`02` §5.3). Absent when the fit computed it and no Factor is
             on a chained grouping; "not available" when the fit predates it, never a table. -->
        <section
          v-if="finerNotAvailable || chainedFactors.length"
          aria-label="Actual versus expected at a finer level"
          class="mt-6 text-sm text-slate-700"
        >
          <h3 class="font-medium">
            Actual versus expected at a finer level
          </h3>
          <p
            v-if="finerNotAvailable"
            class="mt-1"
          >
            Finer level<template v-if="chainedSlugs?.length">
              for {{ chainedSlugs.join(", ") }}
            </template>: not available. This model was fitted before the finer-level actual
            versus expected was stored, and a refit records it.
          </p>
          <template v-else>
            <div
              v-for="entry in chainedFactors"
              :key="entry.factor"
              class="mt-3"
            >
              <label class="flex items-center gap-2">
                <span>Level for {{ entry.factor }}</span>
                <select
                  :value="selectedOf(entry)"
                  :aria-label="`Level for ${entry.factor}`"
                  class="rounded border border-slate-300 px-2 py-1"
                  @change="choose(entry.factor, $event)"
                >
                  <option
                    v-if="hasFitted(entry)"
                    value=""
                  >
                    {{ entry.grouping }} (as fitted)
                  </option>
                  <option
                    v-for="level in entry.levels"
                    :key="level.name"
                    :value="level.name"
                  >
                    {{ level.name }}
                  </option>
                </select>
              </label>
              <table
                v-for="table in finerTables(entry)"
                :key="table.label"
                :aria-label="`${entry.factor} at ${levelCaption(entry)}, ${table.label}`"
                class="mt-2 w-full text-left text-sm"
              >
                <caption class="text-left text-xs uppercase tracking-wide text-slate-500">
                  {{ table.label }}
                </caption>
                <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
                  <tr>
                    <th
                      scope="col"
                      class="py-2 font-medium"
                    >
                      Level
                    </th>
                    <th
                      scope="col"
                      class="py-2 font-medium"
                    >
                      A/E
                    </th>
                    <th
                      scope="col"
                      class="py-2 font-medium"
                    >
                      Actual
                    </th>
                    <th
                      scope="col"
                      class="py-2 font-medium"
                    >
                      Expected
                    </th>
                    <th
                      scope="col"
                      class="py-2 font-medium"
                    >
                      Exposure
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="row in table.rows"
                    :key="row.level"
                    class="border-b border-slate-100"
                  >
                    <th
                      scope="row"
                      class="py-1 font-normal"
                    >
                      {{ row.level }}
                    </th>
                    <td class="py-1 tabular-nums">
                      {{ figure(row.ae) }}
                    </td>
                    <td class="py-1 tabular-nums">
                      {{ figure(row.actual) }}
                    </td>
                    <td class="py-1 tabular-nums">
                      {{ figure(row.expected) }}
                    </td>
                    <td class="py-1 tabular-nums">
                      {{ row.exposure ?? "—" }}
                    </td>
                  </tr>
                  <tr
                    v-if="table.unavailable"
                    class="border-b border-slate-100 text-slate-500"
                  >
                    <th
                      scope="row"
                      class="py-1 font-normal"
                    >
                      not available ({{ table.unavailable.rows }} rows)
                    </th>
                    <td class="py-1 tabular-nums">
                      —
                    </td>
                    <td class="py-1 tabular-nums">
                      {{ figure(table.unavailable.actual) }}
                    </td>
                    <td class="py-1 tabular-nums">
                      {{ figure(table.unavailable.expected) }}
                    </td>
                    <td class="py-1 tabular-nums">
                      {{ table.unavailable.exposure }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </template>
        </section>

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
          :permutation-omitted="diagnostics.gbm.permutation_omitted"
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

        <!-- FR-199. Present only on the second bound of a quantile pair, and a scalar
             record rather than a series: how often this model's prediction crossed its
             counterpart's, and by how much at worst. `QuantileBoundNotice` on the model page
             reads the spec's `interval_for` and says nothing about crossing; this is the
             measurement. Crossing is reported and never repaired (OQ-574). -->
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
