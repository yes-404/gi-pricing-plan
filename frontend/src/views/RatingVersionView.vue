<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink } from "vue-router";

import { ProblemError } from "@/api/problem";
import { getRatingVersion, type RatingVersion } from "@/api/ratingVersions";

const props = defineProps<{ id: string }>();

const rating = ref<RatingVersion | null>(null);
const loading = ref(true);
const problem = ref<ProblemError | null>(null);

onMounted(async () => {
  try {
    rating.value = await getRatingVersion(props.id);
  } catch (error) {
    if (error instanceof ProblemError) problem.value = error;
    else throw error;
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <section class="mx-auto max-w-3xl px-4 py-8">
    <p class="text-sm text-slate-500">
      <RouterLink
        to="/data"
        class="hover:underline"
      >
        Datasets
      </RouterLink>
      <span class="mx-1.5">/</span>
      <RouterLink
        to="/demo"
        class="hover:underline"
      >
        Demo
      </RouterLink>
    </p>

    <template v-if="loading">
      <p class="mt-6 text-sm text-slate-500">
        Loading…
      </p>
    </template>

    <template v-else-if="problem">
      <div
        role="alert"
        class="mt-6 rounded-md border border-red-200 bg-red-50 p-4"
      >
        <p class="text-sm font-medium text-red-800">
          {{ problem.problem.title }}
        </p>
        <p class="mt-1 text-sm text-red-700">
          {{ problem.problem.detail }}
        </p>
      </div>
    </template>

    <template v-else-if="rating">
      <h1 class="mt-4 text-2xl font-semibold">
        {{ rating.slug }} <span class="font-mono text-lg text-slate-500">@{{ rating.version }}</span>
      </h1>
      <dl class="mt-4 grid grid-cols-2 gap-3 text-sm">
        <div>
          <dt class="text-slate-500">
            Status
          </dt>
          <dd class="font-medium">
            {{ rating.status }}
          </dd>
        </div>
        <div>
          <dt class="text-slate-500">
            Pinned model
          </dt>
          <dd class="font-mono">
            {{ rating.model_ref }}
          </dd>
        </div>
        <div>
          <dt class="text-slate-500">
            Dataset version
          </dt>
          <dd class="font-mono">
            {{ rating.dataset_version_id }}
          </dd>
        </div>
        <div>
          <dt class="text-slate-500">
            Created
          </dt>
          <dd>{{ new Date(rating.created_at).toLocaleString() }}</dd>
        </div>
      </dl>
      <p class="mt-6 text-xs text-slate-500">
        The Phase 1b rating version (FR-PLAT-67). Compile, score, rate tables and deployment
        stay Phase 2.
      </p>
    </template>
  </section>
</template>
