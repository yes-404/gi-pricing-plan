<script setup lang="ts">
/**
 * The factor workbench (`02` §5.3, `00` §5.6 — `/factors/:datasetVersionId`).
 *
 * **The interaction requirement is the whole point of this view**, and `02` §5.3 states it
 * outright: the banding and grouping editors must show the *consequence* of an edit before
 * it is saved. An actuary should never have to fit a model to find out whether a grouping
 * was sensible. So every edit here re-evaluates against the real dataset version through
 * FR-MODEL-83's `/evaluate` routes — the numbers on screen are the platform's, computed on
 * the same code path a fit would use, never approximated in the browser.
 *
 * What is deliberately *not* here: drag handles on the boundaries. §5.3 asks for draggable
 * cut points and these are numeric inputs. The requirement they serve — that the
 * consequence is visible before saving — is met either way, and the input is the honest
 * version to ship first because it can express a boundary the mouse cannot land on.
 */
import { computed, onMounted, ref, watch } from "vue";
import { RouterLink } from "vue-router";

import { ProblemError, isProblem } from "@/api/problem";
import { getProfile, type Profile } from "@/api/profiles";
import {
  createBanding,
  createGrouping,
  evaluateBanding,
  evaluateGrouping,
  mergeVerdict,
  proposeBanding,
  proposeGrouping,
  targetLevels,
  withBoundary,
  withMapping,
  type Banding,
  type BandingMethod,
  type Grouping,
  type GroupingMethod,
} from "@/api/transformations";
import { formatDecimalString, getVersionById } from "@/api/versions";

const props = defineProps<{ datasetVersionId: string }>();

const profile = ref<Profile | null>(null);
const datasetId = ref<string | null>(null);
const loading = ref(true);
const problem = ref<ProblemError | null>(null);

/** Which half of the workbench is in front. Both edit the same dataset version. */
const tab = ref<"banding" | "grouping">("banding");

// --- banding -----------------------------------------------------------------------------

const bandingColumn = ref<string>("");
const bandingMethod = ref<BandingMethod>("exposure_quantile");
const bandCount = ref(5);
const banding = ref<Banding | null>(null);
const bandingBusy = ref(false);
const bandingProblem = ref<ProblemError | null>(null);
/** Set while an edited boundary is invalid, so the input can be marked and the last good
 * evaluation held rather than replaced by an error. */
const boundaryRejected = ref<number | null>(null);
const bandingSaved = ref<Banding | null>(null);

const bandTotalExposure = computed(() =>
  (banding.value?.band_stats ?? []).reduce((sum, row) => sum + Number(row.exposure_years), 0),
);

// --- grouping ----------------------------------------------------------------------------

const groupingColumn = ref<string>("");
const groupingMethod = ref<GroupingMethod>("hierarchical_clustering");
const groupCount = ref(4);
const grouping = ref<Grouping | null>(null);
const groupingBusy = ref(false);
const groupingProblem = ref<ProblemError | null>(null);
const groupingSaved = ref<Grouping | null>(null);

const groupTargets = computed(() => (grouping.value ? targetLevels(grouping.value) : []));
const verdict = computed(() => mergeVerdict(grouping.value?.evidence));

const VERDICT_COPY: Record<string, string> = {
  supported: "The data does not distinguish these levels — the merge is supported.",
  borderline: "Borderline: the merge gives up some signal. Worth a sentence in the model document.",
  costly: "The merged levels are genuinely different. This merge discards real signal.",
  untested: "No degrees of freedom saved, so there is nothing to test.",
};

const VERDICT_TONE: Record<string, string> = {
  supported: "border-emerald-200 bg-emerald-50 text-emerald-900",
  borderline: "border-amber-200 bg-amber-50 text-amber-900",
  costly: "border-red-200 bg-red-50 text-red-900",
  untested: "border-slate-200 bg-slate-50 text-slate-700",
};

/** Columns the profile marked as candidate rating factors — `01` FR-DATA-26's one-ways. */
const columns = computed(() => (profile.value?.one_ways ?? []).map((o) => o.column));

async function load(): Promise<void> {
  loading.value = true;
  problem.value = null;
  try {
    const version = await getVersionById(props.datasetVersionId);
    datasetId.value = version.dataset_id;
    profile.value = await getProfile(props.datasetVersionId);
    bandingColumn.value = columns.value[0] ?? "";
    groupingColumn.value = columns.value[0] ?? "";
  } catch (error) {
    if (error instanceof ProblemError) problem.value = error;
    else throw error;
  } finally {
    loading.value = false;
  }
}

function slugFor(column: string, suffix: string): string {
  return `${column.replace(/_/g, "-")}-${suffix}`;
}

async function runBandingProposal(): Promise<void> {
  if (!bandingColumn.value) return;
  bandingBusy.value = true;
  bandingProblem.value = null;
  bandingSaved.value = null;
  try {
    banding.value = await proposeBanding({
      dataset_version_id: props.datasetVersionId,
      column: bandingColumn.value,
      method: bandingMethod.value,
      n_bands: bandCount.value,
      slug: slugFor(bandingColumn.value, String(bandCount.value)),
    });
  } catch (error) {
    if (error instanceof ProblemError) {
      banding.value = null;
      bandingProblem.value = error;
    } else throw error;
  } finally {
    bandingBusy.value = false;
  }
}

/**
 * FR-MODEL-83. The edit's consequence, from the platform, before anything is saved.
 *
 * An invalid move — a boundary crossing its neighbour — is marked and **not** sent: the
 * platform would refuse it correctly with a 422, and a 422 per keystroke is not an editor.
 */
async function moveBoundary(index: number, raw: string): Promise<void> {
  if (!banding.value) return;
  const next = withBoundary(banding.value, index, Number(raw));
  if (next === null) {
    boundaryRejected.value = index;
    return;
  }
  boundaryRejected.value = null;
  bandingBusy.value = true;
  bandingProblem.value = null;
  try {
    banding.value = await evaluateBanding(props.datasetVersionId, next);
  } catch (error) {
    if (error instanceof ProblemError) bandingProblem.value = error;
    else throw error;
  } finally {
    bandingBusy.value = false;
  }
}

async function saveBanding(): Promise<void> {
  if (!banding.value || !datasetId.value) return;
  bandingBusy.value = true;
  bandingProblem.value = null;
  try {
    bandingSaved.value = await createBanding({
      ...banding.value,
      dataset_id: datasetId.value,
    });
  } catch (error) {
    if (error instanceof ProblemError) bandingProblem.value = error;
    else throw error;
  } finally {
    bandingBusy.value = false;
  }
}

async function runGroupingProposal(): Promise<void> {
  if (!groupingColumn.value) return;
  groupingBusy.value = true;
  groupingProblem.value = null;
  groupingSaved.value = null;
  try {
    grouping.value = await proposeGrouping({
      dataset_version_id: props.datasetVersionId,
      column: groupingColumn.value,
      method: groupingMethod.value,
      n_groups: groupCount.value,
      unseen_level_behaviour: "map_to_default",
      slug: slugFor(groupingColumn.value, String(groupCount.value)),
    });
  } catch (error) {
    if (error instanceof ProblemError) {
      grouping.value = null;
      groupingProblem.value = error;
    } else throw error;
  } finally {
    groupingBusy.value = false;
  }
}

/** FR-MODEL-83: re-merge, and show what it cost, before the grouping is saved. */
async function moveLevel(level: string, target: string): Promise<void> {
  if (!grouping.value) return;
  groupingBusy.value = true;
  groupingProblem.value = null;
  try {
    grouping.value = await evaluateGrouping(
      props.datasetVersionId,
      withMapping(grouping.value, level, target),
    );
  } catch (error) {
    if (error instanceof ProblemError) groupingProblem.value = error;
    else throw error;
  } finally {
    groupingBusy.value = false;
  }
}

async function saveGrouping(): Promise<void> {
  if (!grouping.value || !datasetId.value) return;
  groupingBusy.value = true;
  groupingProblem.value = null;
  try {
    groupingSaved.value = await createGrouping({
      ...grouping.value,
      dataset_id: datasetId.value,
    });
  } catch (error) {
    if (error instanceof ProblemError) groupingProblem.value = error;
    else throw error;
  } finally {
    groupingBusy.value = false;
  }
}

watch(() => props.datasetVersionId, () => void load());
onMounted(() => void load());

function share(value: string | number): string {
  const total = bandTotalExposure.value;
  return total > 0 ? `${((Number(value) / total) * 100).toFixed(1)}%` : "—";
}

function isThin(row: { claim_count: number }): boolean {
  // A band nobody can estimate from. Not a platform threshold — FR-MODEL-11's minimums are
  // configured per fit — but the number an actuary scans the column for.
  return row.claim_count < 30;
}

defineExpose({ isProblem });
</script>

<template>
  <section>
    <header class="mb-5">
      <p class="text-sm text-slate-500">
        Factor workbench
      </p>
      <h1 class="mt-1 text-xl font-semibold tracking-tight">
        Bandings and groupings
      </h1>
      <p class="mt-1 text-sm text-slate-600">
        Every number below is computed by the platform against this dataset version, before
        anything is saved.
      </p>
    </header>

    <p
      v-if="loading"
      class="text-sm text-slate-500"
    >
      Loading…
    </p>

    <div
      v-else-if="problem"
      role="alert"
      class="rounded-md border border-red-200 bg-red-50 p-4"
    >
      <p class="font-medium text-red-900">
        {{ problem.problem.title }}
      </p>
      <p
        v-if="problem.problem.detail"
        class="mt-1 text-sm text-red-800"
      >
        {{ problem.problem.detail }}
      </p>
    </div>

    <template v-else>
      <div
        class="mb-5 flex gap-2 border-b border-slate-200"
        role="tablist"
      >
        <button
          v-for="option in (['banding', 'grouping'] as const)"
          :key="option"
          type="button"
          role="tab"
          :aria-selected="tab === option"
          class="-mb-px border-b-2 px-3 py-2 text-sm capitalize"
          :class="
            tab === option
              ? 'border-slate-900 font-medium text-slate-900'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          "
          @click="tab = option"
        >
          {{ option }}
        </button>
      </div>

      <!-- ---------------------------------------------------------------- banding -->
      <div v-show="tab === 'banding'">
        <div class="flex flex-wrap items-end gap-3">
          <label class="text-sm">
            <span class="block text-slate-600">Column</span>
            <select
              v-model="bandingColumn"
              aria-label="Column to band"
              class="mt-1 rounded-md border border-slate-300 px-2 py-1 text-sm"
            >
              <option
                v-for="column in columns"
                :key="column"
                :value="column"
              >
                {{ column }}
              </option>
            </select>
          </label>

          <label class="text-sm">
            <span class="block text-slate-600">Method</span>
            <select
              v-model="bandingMethod"
              aria-label="Banding method"
              class="mt-1 rounded-md border border-slate-300 px-2 py-1 text-sm"
            >
              <option value="exposure_quantile">
                Exposure quantile
              </option>
              <option value="quantile">
                Row quantile
              </option>
              <option value="equal_width">
                Equal width
              </option>
              <option value="credibility">
                Credibility
              </option>
            </select>
          </label>

          <label class="text-sm">
            <span class="block text-slate-600">Bands</span>
            <input
              v-model.number="bandCount"
              type="number"
              min="2"
              max="50"
              aria-label="Number of bands"
              class="mt-1 w-20 rounded-md border border-slate-300 px-2 py-1 text-sm"
            >
          </label>

          <button
            type="button"
            class="rounded-md bg-slate-900 px-3 py-1.5 text-sm text-white disabled:opacity-50"
            :disabled="bandingBusy || !bandingColumn"
            @click="runBandingProposal"
          >
            Propose
          </button>
        </div>

        <div
          v-if="bandingProblem"
          role="alert"
          class="mt-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-900"
        >
          {{ bandingProblem.problem.detail ?? bandingProblem.problem.title }}
        </div>

        <template v-if="banding">
          <p class="mt-5 text-sm text-slate-600">
            <span class="font-medium">{{ banding.labels.length }}</span> bands by
            <span class="font-mono text-xs">{{ banding.method }}</span>. Edit a boundary and
            the statistics below are recomputed against the version (FR-MODEL-83).
          </p>

          <div class="mt-3 flex flex-wrap gap-2">
            <label
              v-for="(boundary, index) in banding.boundaries"
              :key="index"
              class="text-xs"
            >
              <span class="block text-slate-500">cut {{ index }}</span>
              <input
                :value="boundary"
                type="number"
                :disabled="index === 0 || index === banding.boundaries.length - 1"
                :aria-label="`Boundary ${index}`"
                :aria-invalid="boundaryRejected === index"
                class="mt-0.5 w-24 rounded-md border px-2 py-1 tabular-nums disabled:bg-slate-100 disabled:text-slate-400"
                :class="boundaryRejected === index ? 'border-red-400 bg-red-50' : 'border-slate-300'"
                @change="moveBoundary(index, ($event.target as HTMLInputElement).value)"
              >
            </label>
          </div>
          <p
            v-if="boundaryRejected !== null"
            class="mt-2 text-xs text-red-700"
          >
            A boundary cannot cross its neighbours — bands would overlap, and one row would
            belong to two levels. The statistics below are still the last valid cut.
          </p>

          <table class="mt-4 w-full text-sm">
            <caption class="sr-only">
              Band statistics
            </caption>
            <thead class="text-left text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th
                  scope="col"
                  class="py-1.5"
                >
                  Band
                </th>
                <th
                  scope="col"
                  class="py-1.5 text-right"
                >
                  Exposure
                </th>
                <th
                  scope="col"
                  class="py-1.5 text-right"
                >
                  Share
                </th>
                <th
                  scope="col"
                  class="py-1.5 text-right"
                >
                  Claims
                </th>
                <th
                  scope="col"
                  class="py-1.5 text-right"
                >
                  Frequency
                </th>
                <th
                  scope="col"
                  class="py-1.5 text-right"
                >
                  95% interval
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 tabular-nums">
              <tr
                v-for="row in banding.band_stats"
                :key="row.level"
                :class="isThin(row) ? 'bg-amber-50' : ''"
              >
                <td class="py-1.5 font-medium">
                  {{ row.level }}
                </td>
                <td class="py-1.5 text-right">
                  {{ formatDecimalString(row.exposure_years) }}
                </td>
                <td class="py-1.5 text-right text-slate-500">
                  {{ share(row.exposure_years) }}
                </td>
                <td class="py-1.5 text-right">
                  {{ row.claim_count.toLocaleString() }}
                </td>
                <td class="py-1.5 text-right">
                  {{ row.frequency?.toFixed(4) ?? "—" }}
                </td>
                <td class="py-1.5 text-right text-slate-500">
                  <span v-if="row.frequency_ci">
                    {{ row.frequency_ci[0].toFixed(4) }} – {{ row.frequency_ci[1].toFixed(4) }}
                  </span>
                  <span v-else>—</span>
                </td>
              </tr>
            </tbody>
          </table>
          <p class="mt-2 text-xs text-slate-500">
            A shaded row holds fewer than 30 claims — its interval is the column to read, not
            its frequency. FR-MODEL-11's configured minimums are enforced at fit time.
          </p>

          <div class="mt-4 flex items-center gap-3">
            <button
              type="button"
              class="rounded-md border border-slate-300 px-3 py-1.5 text-sm disabled:opacity-50"
              :disabled="bandingBusy"
              @click="saveBanding"
            >
              Save banding
            </button>
            <p
              v-if="bandingSaved"
              class="text-sm text-emerald-800"
            >
              Saved as
              <span class="font-mono text-xs">{{ bandingSaved.slug }}</span>
              version {{ bandingSaved.version }}. Editing it again allocates the next version
              (FR-MODEL-12).
            </p>
          </div>
        </template>
      </div>

      <!-- --------------------------------------------------------------- grouping -->
      <div v-show="tab === 'grouping'">
        <div class="flex flex-wrap items-end gap-3">
          <label class="text-sm">
            <span class="block text-slate-600">Column</span>
            <select
              v-model="groupingColumn"
              aria-label="Column to group"
              class="mt-1 rounded-md border border-slate-300 px-2 py-1 text-sm"
            >
              <option
                v-for="column in columns"
                :key="column"
                :value="column"
              >
                {{ column }}
              </option>
            </select>
          </label>

          <label class="text-sm">
            <span class="block text-slate-600">Method</span>
            <select
              v-model="groupingMethod"
              aria-label="Grouping method"
              class="mt-1 rounded-md border border-slate-300 px-2 py-1 text-sm"
            >
              <option value="hierarchical_clustering">
                Hierarchical clustering
              </option>
              <option value="credibility_weighted">
                Credibility weighted
              </option>
            </select>
          </label>

          <label class="text-sm">
            <span class="block text-slate-600">Groups</span>
            <input
              v-model.number="groupCount"
              type="number"
              min="1"
              max="50"
              aria-label="Number of groups"
              class="mt-1 w-20 rounded-md border border-slate-300 px-2 py-1 text-sm"
            >
          </label>

          <button
            type="button"
            class="rounded-md bg-slate-900 px-3 py-1.5 text-sm text-white disabled:opacity-50"
            :disabled="groupingBusy || !groupingColumn"
            @click="runGroupingProposal"
          >
            Propose
          </button>
        </div>

        <div
          v-if="groupingProblem"
          role="alert"
          class="mt-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-900"
        >
          {{ groupingProblem.problem.detail ?? groupingProblem.problem.title }}
        </div>

        <template v-if="grouping">
          <div
            class="mt-5 rounded-md border p-3 text-sm"
            :class="VERDICT_TONE[verdict]"
            data-testid="merge-verdict"
          >
            <p class="font-medium">
              {{ grouping.evidence?.source_level_count ?? 0 }} levels →
              {{ grouping.evidence?.target_level_count ?? 0 }},
              {{ grouping.evidence?.df_saved ?? 0 }} degrees of freedom saved
            </p>
            <p class="mt-1">
              {{ VERDICT_COPY[verdict] }}
              <span
                v-if="grouping.evidence?.chi2_p_value != null"
                class="tabular-nums"
              >
                (p = {{ grouping.evidence.chi2_p_value.toExponential(2) }})
              </span>
            </p>
            <p
              v-if="grouping.evidence?.deviance_before != null && grouping.evidence?.deviance_after != null"
              class="mt-1 text-xs tabular-nums opacity-80"
            >
              deviance {{ grouping.evidence.deviance_before.toFixed(1) }} →
              {{ grouping.evidence.deviance_after.toFixed(1) }}
            </p>
          </div>

          <table class="mt-4 w-full text-sm">
            <caption class="sr-only">
              Source levels and their target
            </caption>
            <thead class="text-left text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th
                  scope="col"
                  class="py-1.5"
                >
                  Level
                </th>
                <th
                  scope="col"
                  class="py-1.5"
                >
                  Target
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr
                v-for="(target, level) in grouping.mapping"
                :key="level"
              >
                <td class="py-1.5 font-mono text-xs">
                  {{ level }}
                </td>
                <td class="py-1.5">
                  <select
                    :value="target"
                    :aria-label="`Target for ${level}`"
                    class="rounded-md border border-slate-300 px-2 py-1 text-sm"
                    @change="moveLevel(String(level), ($event.target as HTMLSelectElement).value)"
                  >
                    <option
                      v-for="option in groupTargets"
                      :key="option"
                      :value="option"
                    >
                      {{ option }}
                    </option>
                  </select>
                </td>
              </tr>
            </tbody>
          </table>

          <div class="mt-4 flex items-center gap-3">
            <button
              type="button"
              class="rounded-md border border-slate-300 px-3 py-1.5 text-sm disabled:opacity-50"
              :disabled="groupingBusy"
              @click="saveGrouping"
            >
              Save grouping
            </button>
            <p
              v-if="groupingSaved"
              class="text-sm text-emerald-800"
            >
              Saved as
              <span class="font-mono text-xs">{{ groupingSaved.slug }}</span>
              version {{ groupingSaved.version }}.
            </p>
          </div>
        </template>
      </div>

      <p class="mt-8 text-xs text-slate-500">
        <RouterLink
          to="/data"
          class="hover:underline"
        >
          Datasets
        </RouterLink>
      </p>
    </template>
  </section>
</template>
