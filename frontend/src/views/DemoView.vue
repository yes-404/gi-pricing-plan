<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";

import {
  byModule,
  getGuide,
  isOpenable,
  unpublishedByModule,
  type DemoGuide,
} from "@/api/demo";
import { listModels, type Model } from "@/api/models";
import { isProblem, ProblemError } from "@/api/problem";
import { listRatingVersions, type RatingVersion } from "@/api/ratingVersions";

/**
 * The demo entrance (FR-PLAT-53) and its guide (FR-PLAT-54).
 *
 * Everything on this page is **derived** — the views from each spec's §5.3 table checked
 * against the frontend router, the API surface from the published contract, the state from
 * the roadmap's status table. Nothing is written here, because the page's purpose is
 * telling a person what to trust, and a page that could be wrong about that is worse than
 * no page at all.
 */
const guide = ref<DemoGuide | null>(null);
const loading = ref(true);
const disabled = ref(false);
const problem = ref<ProblemError | null>(null);

/** The seeded models and rating version (W7-5) — best-effort: absent when dev auth is off. */
const demoModels = ref<Model[]>([]);
const ratingVersions = ref<RatingVersion[]>([]);
const seededError = ref(false);

const modules = computed(() => (guide.value ? byModule(guide.value) : []));
const built = computed(() => (guide.value?.views ?? []).filter((view) => view.implemented));
const pending = computed(() => (guide.value?.views ?? []).filter((view) => !view.implemented));
const closed = computed(() => (guide.value?.workstreams ?? []).filter((w) => w.closed));
const endpoints = computed(() =>
  (guide.value?.api ?? []).reduce((total, group) => total + (group.endpoints?.length ?? 0), 0),
);
const unpublished = computed(() => guide.value?.unpublished_endpoints ?? []);
const unpublishedGroups = computed(() =>
  guide.value ? unpublishedByModule(guide.value) : [],
);
/**
 * The phase the workstream section actually covers. It covered Phase 1a alone while the
 * page reported "7/7 closed" — a 100 % signal for a plan four phases from done.
 */
const statusPhases = computed(() =>
  [...new Set((guide.value?.workstreams ?? []).map((w) => w.phase))].join(", "),
);

onMounted(async () => {
  try {
    guide.value = await getGuide();
  } catch (error) {
    // A 404 here is not a failure: the entrance exists only where development identity
    // does, and saying "not found" would send the reader looking for a bug.
    if (isProblem(error, "NOT_FOUND")) disabled.value = true;
    else if (error instanceof ProblemError) problem.value = error;
    else throw error;
  }
  // Best-effort, after the guide: the seeded workspace's models and rating version
  // (W7-5). A failure here (auth off, or nothing seeded) is not a guide failure — the
  // section simply shows nothing.
  try {
    const page = await listModels();
    demoModels.value = page.items.filter(
      (model) => model.status === "approved" || model.status === "fitted",
    );
    ratingVersions.value = await listRatingVersions();
  } catch {
    seededError.value = true;
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <section>
    <header class="mb-6">
      <h1 class="text-xl font-semibold tracking-tight">
        What you can drive by hand
      </h1>
      <p class="mt-1 text-sm text-slate-500">
        Derived from the repository on every request — the specs' view tables against the
        router, the published contract, and the roadmap. Nothing here is written down, so
        nothing here can go stale.
      </p>
    </header>

    <p
      v-if="loading"
      class="text-sm text-slate-500"
    >
      Loading…
    </p>

    <p
      v-else-if="disabled"
      class="rounded-md border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700"
    >
      The demo entrance is not enabled here. It exists only where development identity does
      — start the API with <code class="font-mono">GIP_DEV_AUTH_ENABLED=true</code>, which
      refuses to start in a deployed environment.
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

    <template v-else-if="guide">
      <dl class="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div class="rounded-md border border-slate-200 p-3">
          <dt class="text-xs uppercase tracking-wide text-slate-500">
            Views built
          </dt>
          <dd class="mt-1 text-2xl font-semibold">
            {{ built.length }}<span class="text-base text-slate-400">/{{ guide.views?.length ?? 0 }}</span>
          </dd>
        </div>
        <div class="rounded-md border border-slate-200 p-3">
          <dt class="text-xs uppercase tracking-wide text-slate-500">
            Endpoints published
          </dt>
          <dd class="mt-1 text-2xl font-semibold">
            {{ endpoints }}<span
              class="text-base text-slate-400"
            >/{{ endpoints + unpublished.length }}</span>
          </dd>
        </div>
        <div class="rounded-md border border-slate-200 p-3">
          <dt class="text-xs uppercase tracking-wide text-slate-500">
            {{ statusPhases }} workstreams closed
          </dt>
          <dd class="mt-1 text-2xl font-semibold">
            {{ closed.length }}<span class="text-base text-slate-400">/{{ guide.workstreams?.length ?? 0 }}</span>
          </dd>
        </div>
        <div class="rounded-md border border-slate-200 p-3">
          <dt class="text-xs uppercase tracking-wide text-slate-500">
            Not yet functional
          </dt>
          <dd class="mt-1 text-2xl font-semibold text-amber-700">
            {{ pending.length }}
          </dd>
        </div>
      </dl>

      <section class="mt-8">
        <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Start here
        </h2>
        <p class="mt-1 text-sm text-slate-600">
          The freMTPL2 seed leaves a dataset that has been through the failure loop: version
          1 fails validation and is refused promotion, version 2 passes after one
          preparation step. Open the dataset list, then follow a version into its validation
          report — that is Phase 1a's exit criterion, driven by hand.
        </p>
        <ul class="mt-3 flex flex-wrap gap-2">
          <li
            v-for="view in built.filter(isOpenable)"
            :key="view.route"
          >
            <RouterLink
              :to="view.route"
              class="rounded border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50"
            >
              {{ view.name }}
              <span class="ml-1 font-mono text-xs text-slate-500">{{ view.route }}</span>
            </RouterLink>
          </li>
        </ul>
        <p class="mt-2 text-xs text-slate-500">
          The other {{ built.length - built.filter(isOpenable).length }} built views take a
          dataset or version in the path, so they are reached from the list rather than
          linked here — a link with <code class="font-mono">:slug</code> in it would 404.
        </p>
      </section>

      <section
        v-if="!seededError && (demoModels.length > 0 || ratingVersions.length > 0)"
        class="mt-8"
      >
        <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Seeded workspace
        </h2>
        <p class="mt-1 text-sm text-slate-600">
          The freMTPL2 seed fits a GLM and a GBM, compares them, and approves one — the
          Phase 1b modelling half (W7). The approved model is what the rating version pins.
        </p>
        <ul class="mt-3 flex flex-wrap gap-2">
          <li
            v-for="model in demoModels"
            :key="model.id"
          >
            <RouterLink
              :to="`/models/${model.model_family_slug}?version=${model.version}`"
              class="rounded border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50"
            >
              {{ model.model_family_slug }}
              <span class="ml-1 font-mono text-xs text-slate-500">{{ model.status }}</span>
            </RouterLink>
          </li>
          <li
            v-for="rating in ratingVersions"
            :key="rating.id"
          >
            <RouterLink
              :to="`/rating-versions/${rating.id}`"
              class="rounded border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50"
            >
              {{ rating.slug }}
              <span class="ml-1 font-mono text-xs text-slate-500">{{ rating.status }}</span>
            </RouterLink>
          </li>
        </ul>
      </section>

      <section
        v-for="group in modules"
        :key="group.module"
        class="mt-8"
      >
        <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
          {{ group.module }} — {{ group.views.filter((v) => v.implemented).length }} of
          {{ group.views.length }} built
        </h2>
        <table
          :aria-label="`${group.module} views`"
          class="mt-2 w-full text-left text-sm"
        >
          <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th
                scope="col"
                class="py-2 font-medium"
              >
                View
              </th>
              <th
                scope="col"
                class="py-2 font-medium"
              >
                Route
              </th>
              <th
                scope="col"
                class="py-2 font-medium"
              >
                State
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="view in group.views"
              :key="view.route"
              class="border-b border-slate-100 align-top"
            >
              <td class="py-2">
                {{ view.name }}
                <p class="mt-0.5 text-xs text-slate-500">
                  {{ view.contents }}
                </p>
              </td>
              <td class="py-2 font-mono text-xs">
                {{ view.route }}
              </td>
              <!-- "Built" is the router agreeing with the spec, not a claim anyone made
                   about it. The word is deliberately not "done": a routed view can still
                   be thin, and the closure records are where that is stated. -->
              <td class="py-2">
                <span
                  v-if="view.implemented"
                  class="rounded bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-900"
                >built</span>
                <span
                  v-else
                  class="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-600"
                >not yet</span>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <section class="mt-8">
        <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Declared but not published — {{ unpublished.length }} endpoints
        </h2>
        <p class="mt-1 text-xs text-slate-500">
          Each is a route a spec's §5.1 table declares and the published contract does not
          carry. The count above reads {{ endpoints }} of
          {{ endpoints + unpublished.length }} for that reason.
        </p>
        <ul class="mt-2 flex flex-wrap gap-2">
          <li
            v-for="group in unpublishedGroups"
            :key="group.module"
            class="rounded border border-slate-200 px-2 py-1 text-xs"
          >
            <span class="font-medium">{{ group.module }}</span>
            <span class="ml-1 text-slate-500">{{ group.count }}</span>
          </li>
        </ul>
      </section>

      <section class="mt-8">
        <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Workstreams, as the roadmap states them
        </h2>
        <!-- Scoped, because the roadmap gives a status table to some phases and not
             others. An unscoped "7/7 closed" read as a finished project. -->
        <p
          v-if="(guide.phases_without_status ?? []).length"
          class="mt-1 text-xs text-amber-800"
        >
          {{ statusPhases }} only. No status table exists yet for
          {{ (guide.phases_without_status ?? []).join(", ") }} — those phases are ahead,
          not complete.
        </p>
        <ul class="mt-2 space-y-1 text-sm">
          <li
            v-for="workstream in guide.workstreams"
            :key="`${workstream.phase}-${workstream.workstream}`"
            class="flex gap-2"
          >
            <span class="font-mono text-xs text-slate-500">{{ workstream.phase }}</span>
            <span class="font-medium">{{ workstream.workstream }}</span>
            <span class="text-slate-600">{{ workstream.scope }}</span>
            <span
              :class="workstream.closed ? 'text-emerald-800' : 'text-amber-800'"
            >{{ workstream.status }}</span>
          </li>
        </ul>
      </section>

      <p class="mt-8 text-xs text-slate-500">
        Derived from {{ (guide.generated_from ?? []).join(", ") }}.
      </p>
    </template>
  </section>
</template>
