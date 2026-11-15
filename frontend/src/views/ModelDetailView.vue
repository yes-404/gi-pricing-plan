<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";

import {
  ebmFit,
  ebmSpec,
  gbmFit,
  gbmSpec,
  getModel,
  getTransparency,
  relativityInterval,
  spansZero,
  type Coefficient,
  type Model,
  type TransparencyArtifact,
} from "@/api/models";
import { isProblem, ProblemError } from "@/api/problem";
import EbmShapePanel from "@/components/EbmShapePanel.vue";
import GbmFitPanel from "@/components/GbmFitPanel.vue";
import QuantileBoundNotice from "@/components/QuantileBoundNotice.vue";
import SurrogateNotice from "@/components/SurrogateNotice.vue";
import TransparencyPanel from "@/components/TransparencyPanel.vue";

const props = defineProps<{ slug: string; version?: string }>();

const model = ref<Model | null>(null);
const loading = ref(true);
const problem = ref<ProblemError | null>(null);

/**
 * **The GLM arm only.** `02` §4.4's spec and fit result are tagged unions from the GBM
 * slice on, and this view reads coefficients, relativities and a convergence flag — none
 * of which a booster has. Narrowing here rather than casting is what makes the compiler,
 * not a reviewer, the thing that notices when the GBM view is still missing: every
 * consumer below keeps its GLM types, and a non-GLM model renders the header and nothing
 * that would be a lie.
 *
 * The GBM detail view is WK-664's (`02` §5.3), together with the transparency artifact that
 * is a GBM's answer to a relativity table (FR-133).
 */
const glmSpec = computed(() => {
  const spec = model.value?.spec ?? null;
  return spec?.model_type === "glm" ? spec : null;
});
const fit = computed(() => {
  const result = model.value?.fit_result ?? null;
  return result?.model_type === "glm" ? result : null;
});
const gbm = computed(() => (model.value ? gbmSpec(model.value) : null));
const ebm = computed(() => (model.value ? ebmSpec(model.value) : null));
const gbmResult = computed(() => (model.value ? gbmFit(model.value) : null));
const ebmResult = computed(() => (model.value ? ebmFit(model.value) : null));

/**
 * Fitted is a property of the Model, not of the arm the reader happens to be looking at.
 * `fit` above is the GLM narrowing and is null for every booster ever fitted; asking it
 * whether a model is fitted made the page assert the opposite of the truth for two arms of
 * the three.
 */
const fitted = computed(() => model.value?.fit_result != null);

const coefficients = computed<Coefficient[]>(() => fit.value?.coefficients ?? []);
const relativities = computed(() => Object.entries(fit.value?.relativities ?? {}));

/**
 * FR-2143: each level a Factor can produce that this fit has no relativity for. `null` is "not
 * recorded" (a model fitted before the report existed) and `[]` is "none": never one for the other.
 */
const REACH_WORDS: Record<string, string> = {
  null_value: "a missing value",
  below_range: "a value below the first boundary",
  above_range: "a value above the last boundary",
  grouping_target: "a Grouping target level",
};
const unseenGaps = computed(() => fit.value?.unseen_level_gaps ?? null);
/** The interaction terms: `null` is "not recorded", `[]` is "no interaction term" (FR-2143). */
const cellReports = computed(() => fit.value?.unseen_cell_reports ?? null);
function reachedBy(reasons: readonly string[]): string {
  return reasons.map((reason) => REACH_WORDS[reason] ?? reason).join(" or ");
}
const libraries = computed(() =>
  Object.entries(fit.value?.library_versions ?? {})
    .map(([name, version]) => `${name} ${version}`)
    .join(", "),
);

/**
 * `02` R5: every estimate carries uncertainty, so the screen shows it rather than a column
 * of point estimates. A relativity of 1.72 on forty rows and one on four hundred thousand
 * are different claims, and a table that renders them identically invites the wrong one.
 */
function formatInterval([low, high]: [number, number]): string {
  return `${low.toFixed(3)} – ${high.toFixed(3)}`;
}

const artifact = ref<TransparencyArtifact | null>(null);
const transparencyState = ref<"loading" | "ready" | "absent">("loading");

/**
 * FR-132 makes the transparency artifact an obligation for a non-GLM Model, so this is
 * not asked for a GLM — including a GLM surrogate, which is a GLM. A missing artifact is a
 * state and not a failure: the model simply has none built yet, and this is the only call on
 * the page allowed to fail without reaching the error banner.
 *
 * Branched on the code and not the status, as `ProblemError` requires: several codes share a
 * status, and a status branch here would swallow any future 404-shaped refusal as "no
 * artifact yet". The endpoint raises `NOT_FOUND` for the one case this handles.
 */
async function loadTransparency(loaded: Model): Promise<void> {
  if (loaded.spec.model_type === "glm") {
    transparencyState.value = "absent";
    return;
  }
  try {
    artifact.value = await getTransparency(loaded.id);
    transparencyState.value = "ready";
  } catch (error) {
    if (isProblem(error, "NOT_FOUND")) transparencyState.value = "absent";
    else throw error;
  }
}

onMounted(async () => {
  try {
    model.value = await getModel(props.slug, props.version ? Number(props.version) : undefined);
  } catch (error) {
    if (error instanceof ProblemError) problem.value = error;
    else throw error;
  } finally {
    loading.value = false;
  }
  // After the model resolves and after `loading` clears: the page renders the model between
  // the two fetches rather than holding a spinner until both land.
  if (model.value) await loadTransparency(model.value);
});
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
      </p>
      <h1 class="mt-1 text-xl font-semibold tracking-tight">
        {{ slug }}
      </h1>
      <p
        v-if="model"
        class="mt-1 text-sm text-slate-500"
      >
        version {{ model.version }} · {{ model.status }} ·
        <template v-if="glmSpec">
          {{ glmSpec.family }} / {{ glmSpec.link }} link
        </template>
        <template v-else-if="gbm">
          {{ gbm.model_type }} ·
          {{ gbm.objective.kind === "builtin" ? gbm.objective.name : gbm.objective.ref }}
        </template>
        <template v-else-if="ebm">
          ebm · {{ ebm.objective }} · identity link
        </template>
        <template v-else>
          {{ model.spec.model_type }}
        </template> ·
        response <span class="font-mono">{{ model.spec.response_column }}</span>
      </p>

      <!-- FR-137/141. Shared with the diagnostics view, where the same warning has to
           carry more weight: there a surrogate's A/E, residuals and lift are all read as fit
           to experience unless the page says otherwise. -->
      <SurrogateNotice :approximates-model-id="glmSpec?.approximates_model_id ?? null" />

      <!-- Nothing else in the app reaches the diagnostics view, and a view nothing links to
           is not delivered. The version is carried so the page shows this model's evidence
           and not the latest fit's. -->
      <RouterLink
        v-if="model"
        :to="{
          name: 'model-diagnostics',
          params: { slug },
          query: { version: String(model.version) },
        }"
        class="mt-2 inline-block text-sm text-sky-700 hover:underline"
      >
        Diagnostics
      </RouterLink>

      <!-- Nothing else in the app reaches the predict screen, and a screen nothing
           links to is not delivered. -->
      <RouterLink
        v-if="model"
        :to="{
          name: 'model-predict',
          params: { slug },
          query: { version: String(model.version) },
        }"
        class="mt-2 inline-block text-sm text-sky-700 hover:underline"
      >
        Predict
      </RouterLink>
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

    <template v-else-if="model">
      <!-- Above the arm panels, not inside one: the notice is about what this whole page
           *is*, and it applies whether or not the bound has finished fitting. -->
      <QuantileBoundNotice :model="model" />

      <p
        v-if="!fitted"
        class="rounded-md border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700"
      >
        This model is reserved but not yet fitted. The fit runs as a Job; its coefficients
        appear here when it finishes.
      </p>

      <template v-else-if="fit">
        <dl class="grid grid-cols-2 gap-4 sm:grid-cols-4">
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
              Terms
            </dt>
            <dd class="mt-1 text-2xl font-semibold">
              {{ coefficients.length }}
            </dd>
          </div>
          <div class="rounded-md border border-slate-200 p-3">
            <dt class="text-xs uppercase tracking-wide text-slate-500">
              Converged
            </dt>
            <dd class="mt-1 text-2xl font-semibold">
              {{ fit.converged ? "yes" : "no" }}
            </dd>
          </div>
          <div class="rounded-md border border-slate-200 p-3">
            <dt class="text-xs uppercase tracking-wide text-slate-500">
              Fit time
            </dt>
            <dd class="mt-1 text-2xl font-semibold">
              {{ fit.fit_seconds }}s
            </dd>
          </div>
        </dl>

        <section class="mt-8">
          <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Coefficients
          </h2>
          <p class="mt-1 text-xs text-slate-500">
            Every estimate with its 95 % interval (`02` R5). An interval spanning zero has
            not been distinguished from no effect at all, and is marked.
          </p>
          <table
            aria-label="Coefficients"
            class="mt-2 w-full text-left text-sm"
          >
            <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th
                  scope="col"
                  class="py-2 font-medium"
                >
                  Term
                </th>
                <th
                  scope="col"
                  class="py-2 font-medium"
                >
                  Estimate
                </th>
                <th
                  scope="col"
                  class="py-2 font-medium"
                >
                  Std error
                </th>
                <th
                  scope="col"
                  class="py-2 font-medium"
                >
                  95 % interval
                </th>
                <th
                  scope="col"
                  class="py-2 font-medium"
                >
                  Relativity
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="coefficient in coefficients"
                :key="coefficient.term"
                class="border-b border-slate-100"
              >
                <td class="py-2 font-mono text-xs">
                  {{ coefficient.term }}
                </td>
                <td class="py-2 font-mono text-xs">
                  {{ coefficient.estimate.toFixed(4) }}
                </td>
                <td class="py-2 font-mono text-xs text-slate-600">
                  {{ coefficient.std_error.toFixed(4) }}
                </td>
                <td class="py-2 font-mono text-xs">
                  {{ formatInterval(coefficient.ci_95 as [number, number]) }}
                  <span
                    v-if="spansZero(coefficient)"
                    class="ml-1 rounded bg-amber-100 px-1.5 py-0.5 text-amber-900"
                  >spans zero</span>
                </td>
                <td class="py-2 font-mono text-xs">
                  <template v-if="coefficient.relativity != null">
                    {{ coefficient.relativity.toFixed(3) }}
                    <span class="text-slate-400">
                      ({{ formatInterval(relativityInterval(coefficient)) }})
                    </span>
                  </template>
                  <span
                    v-else
                    class="text-slate-400"
                  >—</span>
                </td>
              </tr>
            </tbody>
          </table>
        </section>

        <section
          v-if="fit"
          class="mt-8"
          aria-label="Levels this fit never saw"
        >
          <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Levels this fit never saw
          </h2>
          <p
            v-if="unseenGaps === null"
            class="mt-2 text-sm text-slate-600"
          >
            Not recorded: this model was fitted before the report existed.
          </p>
          <p
            v-else-if="unseenGaps.length === 0"
            class="mt-2 text-sm text-slate-600"
          >
            None among the missing-value levels of banded factors and the target levels of
            groupings. A plain categorical level the fit never saw is not listed here: a quote
            with one is refused, unless the factor declares “map to base”.
          </p>
          <ul
            v-else
            class="mt-2 space-y-1 text-sm text-slate-700"
          >
            <li
              v-for="gap in unseenGaps"
              :key="`${gap.factor}/${gap.level}`"
            >
              {{ gap.factor }}: the level “{{ gap.level }}” is produced by
              {{ reachedBy(gap.reached_by) }}, and this fit has no relativity for it. A quote
              that reaches it is refused, unless the factor declares “map to base”.
            </li>
          </ul>
        </section>

        <section
          v-if="fit"
          class="mt-8"
          aria-label="Interaction cells this fit never saw"
        >
          <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Interaction cells this fit never saw
          </h2>
          <p
            v-if="cellReports === null"
            class="mt-2 text-sm text-slate-600"
          >
            Not recorded: this model was fitted before the report existed.
          </p>
          <p
            v-else-if="cellReports.length === 0"
            class="mt-2 text-sm text-slate-600"
          >
            This fit has no interaction term.
          </p>
          <ul
            v-else
            class="mt-2 space-y-1 text-sm text-slate-700"
          >
            <li
              v-for="report in cellReports"
              :key="report.factor"
            >
              <template v-if="report.state === 'not_examined'">
                {{ report.factor }}: not examined. The cells cannot be computed from what the fit
                holds (a nested interaction, a missing artifact, or a level that contains the cell
                separator), so no cell is counted. A quote in an unseen cell is refused, unless
                the factor declares “map to base”.
              </template>
              <template v-else-if="report.state === 'lower_bound'">
                <template v-if="report.unfitted === 0">
                  {{ report.factor }}: every combination of the levels this fit saw has a
                  relativity.
                </template>
                <template v-else>
                  {{ report.factor }}: at least {{ report.unfitted }} combinations of levels this
                  fit saw have no relativity.
                  <template v-if="report.examples.length > 0">
                    The first {{ report.examples.length }} (at most {{ report.example_cap }} are
                    shown): {{ report.examples.join("; ") }}.
                  </template>
                  <template v-else>
                    There are too many to name (not enumerated).
                  </template>
                  A quote in such a combination is refused, unless the factor declares “map to
                  base”.
                </template>
                Levels this fit never saw at all are not counted.
              </template>
              <template v-else-if="report.unfitted === 0">
                {{ report.factor }}: all {{ report.producible }} cells its operands can produce
                have a relativity in this fit.
              </template>
              <template v-else>
                {{ report.factor }}: {{ report.unfitted }} of {{ report.producible }} cells its
                operands can produce have no relativity in this fit.
                <template v-if="report.state === 'count_only'">
                  There are too many to name (not enumerated).
                </template>
                <template v-else>
                  The first {{ report.examples.length }} (at most {{ report.example_cap }} are
                  shown): {{ report.examples.join("; ") }}.
                </template>
                A quote in such a cell is refused, unless the factor declares “map to base”.
              </template>
            </li>
          </ul>
        </section>

        <section
          v-for="[factor, levels] in relativities"
          :key="factor"
          class="mt-8"
        >
          <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
            {{ factor }} — relativities
          </h2>
          <table
            :aria-label="`${factor} relativities`"
            class="mt-2 w-full text-left text-sm"
          >
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
                  Effect
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
              <!-- The base level is shown, at 1.000 and marked. Omitting it is how a
                   reader ends up believing a factor has one fewer level than it has. -->
              <tr
                v-for="level in levels"
                :key="level.level"
                class="border-b border-slate-100"
              >
                <td class="py-2">
                  {{ level.level }}
                  <span
                    v-if="level.is_base"
                    class="ml-2 rounded bg-slate-200 px-1.5 py-0.5 text-xs text-slate-700"
                  >base</span>
                </td>
                <!-- A relativity is `exp(β)` — a reading of a multiplicative model, and
                     absent under `logit` or `identity`. Showing 1.000 there said "no
                     effect" for a factor spanning eighteen log-odds; the coefficient is
                     what those links have. -->
                <td class="py-2 font-mono text-xs">
                  <template v-if="level.relativity != null">
                    {{ level.relativity.toFixed(3) }}
                  </template>
                  <template v-else-if="level.estimate != null">
                    {{ level.estimate.toFixed(4) }}
                    <span class="text-slate-400">on the link scale</span>
                  </template>
                  <span
                    v-else
                    class="text-slate-400"
                  >—</span>
                </td>
                <td class="py-2 font-mono text-xs text-slate-600">
                  {{ level.exposure != null ? level.exposure.toFixed(1) : "—" }}
                </td>
              </tr>
            </tbody>
          </table>
        </section>

        <p class="mt-8 text-xs text-slate-500">
          Fitted with {{ libraries }}.
          A Model is immutable once fitted (`02` R2): refitting produces a new version, never
          new coefficients on this one.
        </p>
      </template>

      <template v-else-if="gbm && gbmResult">
        <GbmFitPanel
          :spec="gbm"
          :fit="gbmResult"
        />
      </template>

      <template v-else-if="ebm && ebmResult">
        <EbmShapePanel
          :spec="ebm"
          :fit="ebmResult"
        />
      </template>

      <!-- Not for a GLM: FR-132 makes the artifact an obligation for the non-GLM arms,
           and a GLM surrogate is a GLM. -->
      <TransparencyPanel
        v-if="model.spec.model_type !== 'glm'"
        :artifact="artifact"
        :state="transparencyState"
      />
    </template>
  </section>
</template>
