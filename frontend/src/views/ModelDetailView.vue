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
 * The GBM detail view is W6b's (`02` §5.3), together with the transparency artifact that
 * is a GBM's answer to a relativity table (FR-MODEL-34).
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
 * FR-MODEL-33 makes the transparency artifact an obligation for a non-GLM Model, so this is
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

      <!-- FR-MODEL-96/102. A surrogate is a GLM in every visible respect — family, link,
           coefficients, relativities — so nothing else on this page distinguishes one, and
           its R² and residuals are read as fit to experience unless the page says otherwise.
           No link: the id is not resolvable to a slug from this response (§6, E1). -->
      <p
        v-if="glmSpec?.approximates_model_id"
        class="mt-2 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
      >
        This model is a GLM approximation of model
        <span class="font-mono text-xs">{{ glmSpec.approximates_model_id }}</span>. Its
        diagnostics are measured against that model's predictions, not against observed
        claims.
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

      <!-- Not for a GLM: FR-MODEL-33 makes the artifact an obligation for the non-GLM arms,
           and a GLM surrogate is a GLM. -->
      <TransparencyPanel
        v-if="model.spec.model_type !== 'glm'"
        :artifact="artifact"
        :state="transparencyState"
      />
    </template>
  </section>
</template>
