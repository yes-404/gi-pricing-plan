<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";

import {
  getModel,
  relativityInterval,
  spansZero,
  type Coefficient,
  type Model,
} from "@/api/models";
import { ProblemError } from "@/api/problem";

const props = defineProps<{ slug: string; version?: string }>();

const model = ref<Model | null>(null);
const loading = ref(true);
const problem = ref<ProblemError | null>(null);

const fit = computed(() => model.value?.fit_result ?? null);
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

onMounted(async () => {
  try {
    model.value = await getModel(props.slug, props.version ? Number(props.version) : undefined);
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
        {{ model.spec.family }} / {{ model.spec.link }} link ·
        response <span class="font-mono">{{ model.spec.response_column }}</span>
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
      <p
        v-if="!fit"
        class="rounded-md border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700"
      >
        This model is reserved but not yet fitted. The fit runs as a Job; its coefficients
        appear here when it finishes.
      </p>

      <template v-else>
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
                  Relativity
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
                <td class="py-2 font-mono text-xs">
                  {{ level.relativity.toFixed(3) }}
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
    </template>
  </section>
</template>
