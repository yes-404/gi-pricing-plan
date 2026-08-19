<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";

import { listVersions } from "@/api/datasets";
import { ProblemError, isProblem } from "@/api/problem";
import {
  compareProfiles,
  getOneWay,
  getProfile,
  type ColumnComparison,
  type LevelCount,
  type OneWaySummary,
  type Profile,
  type ProfileComparison,
} from "@/api/profiles";
import { formatDecimalString, formatMinor, getVersion, type DatasetVersion } from "@/api/versions";
import ColumnDrift from "@/components/ColumnDrift.vue";
import HistogramChart from "@/components/HistogramChart.vue";
import OneWayChart from "@/components/OneWayChart.vue";

const props = defineProps<{ slug: string; version: string; currency?: string }>();

const profile = ref<Profile | null>(null);
const selected = ref<string | null>(null);
const oneWay = ref<OneWaySummary | null>(null);
const oneWayMissing = ref(false);
const loading = ref(true);
const problem = ref<ProblemError | null>(null);
const versionId = ref<string | null>(null);
const siblings = ref<DatasetVersion[]>([]);
const truncated = ref(false);
const referenceId = ref<string | null>(null);
const comparison = ref<ProfileComparison | null>(null);
const referenceMissingProfile = ref(false);

const route = useRoute();
const router = useRouter();

const currency = computed(() => props.currency ?? "GBP");
const rateable = computed(() => (profile.value?.one_ways ?? []).map((o) => o.column));

const referenceLabel = computed(() => {
  const chosen = siblings.value.find((v) => v.id === referenceId.value);
  return chosen ? `v${chosen.version}` : "";
});

/**
 * The `<select>`'s own value can only ever be a plain string — a native `<option>` with
 * no `value` attribute falls back to its text content ("No comparison"), not `""`, so
 * binding `referenceId` (which is `null` for "no comparison") to the `<select>` directly
 * would leave that option's element value reading as its label rather than empty. This
 * computed is the one place that translates between the DOM's `""` and the model's `null`
 * — `referenceId` itself stays `Ref<string | null>` for Task 4's comparison fetch.
 */
const referenceSelection = computed<string>({
  get: () => referenceId.value ?? "",
  set: (value) => {
    referenceId.value = value === "" ? null : value;
  },
});

/**
 * A chip's label. `level` is nullable (FR-DATA-49): a genuine missing level renders as
 * "—", the same absent-value mark used everywhere else in this view — never the empty
 * string, never the literal word "null". `exposure_years` is an exact decimal string and
 * is rendered, never parsed; it is appended only when the level actually carries one —
 * `null` means the dataset version carried no exposure column at all, which is different
 * from a level having zero exposure.
 */
function chipLabel(item: LevelCount): string {
  const parts = [`${item.level ?? "—"} · ${item.count.toLocaleString()}`];
  if (item.exposure_years != null) parts.push(formatDecimalString(item.exposure_years));
  return parts.join(" · ");
}

async function load(): Promise<void> {
  loading.value = true;
  problem.value = null;
  try {
    const version = await getVersion(props.slug, Number(props.version));
    versionId.value = version.id;
    profile.value = await getProfile(version.id);
    selected.value = rateable.value[0] ?? null;
  } catch (error) {
    if (error instanceof ProblemError) problem.value = error;
    else throw error;
  } finally {
    loading.value = false;
  }

  // The profile itself failed to load — there is nothing to compare, and the error page
  // above already covers it.
  if (!versionId.value) return;

  try {
    // `MAX_LIMIT` is 200 and versions come back newest-first, so one page is the selector's
    // universe. If there is a cursor left, say so rather than silently offering a subset.
    const page = await listVersions(props.slug, { limit: 200 });
    siblings.value = page.items.filter((v) => v.id !== versionId.value);
    truncated.value = page.next_cursor != null;

    // `?against=<version number>`, not an id: the URL is something an actuary reads and
    // sends, and a version number is what the rest of the app routes on. A version with no
    // profile is ignored rather than honoured — a stale link must not put the view into a
    // state the endpoint refuses.
    const wanted = typeof route.query.against === "string" ? route.query.against : null;
    const seeded = siblings.value.find((v) => String(v.version) === wanted);
    if (seeded?.profile_id != null) {
      referenceId.value = seeded.id;
    } else {
      referenceId.value = null;
      if (seeded) {
        // `seeded` names a real sibling with no stored profile — the endpoint would 404
        // for it, so the address bar must not keep advertising a comparison the view is
        // refusing. (Setting `referenceId` above did not change it from its initial
        // `null`, so the write-back watcher never fires on its own.)
        void router.replace({ query: { ...route.query, against: undefined } });
      }
    }
  } catch (error) {
    // The picker is auxiliary: a failing versions list must degrade to "no comparison
    // available" rather than blank an already-loaded profile.
    if (!(error instanceof ProblemError)) throw error;
  }
}

watch(selected, async (column) => {
  oneWay.value = null;
  oneWayMissing.value = false;
  if (!column || !versionId.value) return;
  try {
    oneWay.value = await getOneWay(versionId.value, column);
  } catch (error) {
    // FR-DATA-27: a column with no *stored* one-way is an answer, not a failure. The
    // platform refuses to compute one on request, and so does this.
    if (isProblem(error, "NOT_FOUND")) oneWayMissing.value = true;
    else throw error;
  }
});

watch(referenceId, (id) => {
  const chosen = siblings.value.find((v) => v.id === id);
  void router.replace({
    query: {
      ...route.query,
      ...(chosen ? { against: String(chosen.version) } : { against: undefined }),
    },
  });
});

watch(referenceId, async (id) => {
  comparison.value = null;
  referenceMissingProfile.value = false;
  if (!id || !versionId.value) return;
  try {
    comparison.value = await compareProfiles(versionId.value, id);
  } catch (error) {
    // A reference with no stored profile is an answer, the same as FR-DATA-27's missing
    // one-way: the picker disables those versions, so reaching here means a stale or
    // hand-edited link. It explains itself and leaves the rest of the view intact.
    if (isProblem(error, "NOT_FOUND")) referenceMissingProfile.value = true;
    else throw error;
  }
});

/**
 * The comparison entry for a column, if there is one.
 *
 * Three answers, not two. `compare_profiles` **skips** a column the reference profile does
 * not have, so a missing entry means "this column is new in this version" — which is a
 * finding, not an absence. `undefined` means no comparison has been loaded at all.
 */
function driftFor(name: string): ColumnComparison | null | undefined {
  if (!comparison.value) return undefined;
  return comparison.value.columns.find((c) => c.column === name) ?? null;
}

onMounted(() => void load());
</script>

<template>
  <section>
    <header class="mb-5">
      <p class="text-sm text-slate-500">
        <RouterLink
          to="/data"
          class="hover:underline"
        >
          Datasets
        </RouterLink>
        <span class="mx-1.5">/</span>{{ slug }}<span class="mx-1.5">/</span>
        <RouterLink
          :to="`/data/${slug}/v/${version}`"
          class="hover:underline"
        >
          v{{ version }}
        </RouterLink>
      </p>
      <h1 class="mt-1 text-xl font-semibold tracking-tight">
        Profile
      </h1>
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
      <p
        v-if="problem.traceId"
        class="mt-2 font-mono text-xs text-red-700"
      >
        trace {{ problem.traceId }}
      </p>
    </div>

    <template v-else-if="profile">
      <p class="text-sm text-slate-600 tabular-nums">
        {{ profile.row_count.toLocaleString() }} rows ·
        {{ (profile.columns ?? []).length }} columns ·
        {{ rateable.length }} candidate rating factors
      </p>

      <section class="mt-6">
        <div class="flex items-center gap-3">
          <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Drift
          </h2>
          <select
            v-if="siblings.length"
            v-model="referenceSelection"
            aria-label="Compare against"
            class="rounded-md border border-slate-300 px-2 py-1 text-sm"
          >
            <option value="">
              No comparison
            </option>
            <!-- A version with no stored profile cannot be compared against: the endpoint
                 answers 404 and `profile_id` already says so, so it is shown as unavailable
                 rather than offered and then explained. -->
            <option
              v-for="sibling in siblings"
              :key="sibling.id"
              :value="sibling.id"
              :disabled="sibling.profile_id == null"
            >
              v{{ sibling.version }}{{ sibling.profile_id == null ? " (no profile)" : "" }}
            </option>
          </select>
          <p
            v-else
            class="text-sm text-slate-500"
          >
            No other version of this dataset to compare against.
          </p>
        </div>
        <p
          v-if="truncated"
          class="mt-2 text-xs text-slate-500"
        >
          Showing the 200 most recent versions.
        </p>
        <p
          v-if="referenceMissingProfile"
          class="mt-2 text-sm text-slate-500"
        >
          {{ referenceLabel }} has no profile to compare against. Profiling runs after a
          successful ingestion (FR-DATA-25).
        </p>
        <p
          v-else-if="comparison"
          class="mt-2 text-sm text-slate-600 tabular-nums"
        >
          <!-- A float ratio, not an exact decimal: it is `current.row_count / reference.row_count`
               computed in float64 by `compare_profiles`, so it is shown as the statistic it is. -->
          ×{{ comparison.row_count_ratio?.toFixed(3) ?? "—" }} rows vs {{ referenceLabel }}
        </p>
      </section>

      <section
        v-if="rateable.length"
        class="mt-6"
      >
        <div class="flex items-center gap-3">
          <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
            One-way
          </h2>
          <select
            v-model="selected"
            aria-label="Rating factor"
            class="rounded-md border border-slate-300 px-2 py-1 text-sm"
          >
            <option
              v-for="column in rateable"
              :key="column"
              :value="column"
            >
              {{ column }}
            </option>
          </select>
        </div>

        <p
          v-if="oneWayMissing"
          class="mt-3 text-sm text-slate-500"
        >
          No stored one-way for this column. FR-DATA-27 reads them from the Profile and
          never computes one on request.
        </p>
        <template v-else-if="oneWay">
          <OneWayChart
            :summary="oneWay"
            class="mt-3"
          />
          <table class="mt-3 w-full text-left text-sm">
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
                  class="py-2 text-right font-medium"
                >
                  Exposure
                </th>
                <th
                  scope="col"
                  class="py-2 text-right font-medium"
                >
                  Claims
                </th>
                <th
                  scope="col"
                  class="py-2 text-right font-medium"
                >
                  Incurred
                </th>
                <th
                  scope="col"
                  class="py-2 text-right font-medium"
                >
                  Frequency
                </th>
                <th
                  scope="col"
                  class="py-2 text-right font-medium"
                >
                  Severity
                </th>
                <th
                  scope="col"
                  class="py-2 text-right font-medium"
                >
                  Burning cost
                </th>
              </tr>
            </thead>
            <tbody class="tabular-nums">
              <tr
                v-for="row in oneWay.rows"
                :key="row.level"
                class="border-b border-slate-100"
              >
                <td class="py-2 font-medium">
                  {{ row.level }}
                </td>
                <!-- Exact decimal, formatted from the string and never parsed. -->
                <td class="py-2 text-right">
                  {{ formatDecimalString(row.exposure_years) }}
                </td>
                <td class="py-2 text-right">
                  {{ row.claim_count.toLocaleString() }}
                </td>
                <!-- The one `_minor` field on this row that is an exact amount. -->
                <td class="py-2 text-right">
                  {{ formatMinor(row.claim_amount_minor, currency) }}
                </td>
                <td class="py-2 text-right">
                  {{ row.frequency?.toFixed(4) ?? "—" }}
                </td>
                <!-- `mean_severity` and `mean_burning_cost` are **float ratios**, not
                     amounts: amount ÷ claims and amount ÷ exposure. Formatting them as
                     currency would imply an exactness they do not have, so they are shown
                     as the statistics they are. Still expressed in minor units — only the
                     name changed (FR-DATA-46) — so the `/ 100` scaling stays. -->
                <td class="py-2 text-right">
                  {{ row.mean_severity == null ? "—" : (row.mean_severity / 100).toFixed(2) }}
                </td>
                <td class="py-2 text-right">
                  {{ row.mean_burning_cost == null ? "—" : (row.mean_burning_cost / 100).toFixed(2) }}
                </td>
              </tr>
            </tbody>
          </table>
        </template>
      </section>

      <section class="mt-8">
        <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Columns
        </h2>
        <div class="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <article
            v-for="column in profile.columns"
            :key="column.name"
            class="rounded-md border border-slate-200 p-3"
          >
            <header class="flex items-baseline gap-2">
              <h3 class="font-mono text-sm font-medium">
                {{ column.name }}
              </h3>
              <span class="text-xs text-slate-500">{{ column.semantic_type }}</span>
              <!-- Uncoloured, always: the dtype label is not a PSI band. `ColumnDrift`
                   below carries the band, once a comparison is loaded. -->
              <span class="ml-auto text-xs text-slate-500">{{ column.dtype }}</span>
            </header>
            <dl class="mt-2 grid grid-cols-2 gap-x-3 gap-y-1 text-xs tabular-nums">
              <dt class="text-slate-500">
                distinct
              </dt>
              <dd>{{ column.distinct_count.toLocaleString() }}</dd>
              <dt class="text-slate-500">
                nulls
              </dt>
              <dd>{{ (column.null_rate * 100).toFixed(2) }}%</dd>
              <template v-if="column.mean != null">
                <dt class="text-slate-500">
                  mean
                </dt>
                <dd>{{ column.mean.toFixed(3) }}</dd>
                <dt class="text-slate-500">
                  range
                </dt>
                <dd>{{ column.minimum }} – {{ column.maximum }}</dd>
              </template>
            </dl>
            <ColumnDrift :drift="driftFor(column.name)" />
            <!-- FR-DATA-48. Only continuous columns carry one, so the card shows it only
                 when the profile computed one. -->
            <HistogramChart
              v-if="column.histogram"
              :histogram="column.histogram"
              class="mt-2"
            />
            <ul
              v-if="(column.top_levels ?? []).length"
              class="mt-2 flex flex-wrap gap-1"
            >
              <li
                v-for="(item, index) in (column.top_levels ?? []).slice(0, 6)"
                :key="index"
                class="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-xs text-slate-700"
              >
                {{ chipLabel(item) }}
              </li>
            </ul>
          </article>
        </div>
      </section>
    </template>
  </section>
</template>
