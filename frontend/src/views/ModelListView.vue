<script setup lang="ts">
import { onMounted, ref } from "vue";

import { listModels, type Model } from "@/api/models";

const models = ref<Model[]>([]);
const loadFailure = ref<string | null>(null);

onMounted(async () => {
  try {
    const page = await listModels();
    models.value = page.items;
  } catch (error) {
    loadFailure.value = error instanceof Error ? error.message : String(error);
  }
});
</script>

<template>
  <section>
    <header class="mb-5 flex items-center justify-between">
      <h1 class="text-xl font-semibold tracking-tight">
        Models
      </h1>
      <div class="flex gap-3">
        <RouterLink
          to="/models/new"
          class="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50"
        >
          New model
        </RouterLink>
        <RouterLink
          to="/models/compare"
          class="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50"
        >
          Compare
        </RouterLink>
      </div>
    </header>

    <p
      v-if="loadFailure"
      class="text-sm text-red-600"
    >
      {{ loadFailure }}
    </p>
    <p
      v-else-if="models.length === 0"
      class="text-sm text-slate-500"
    >
      No models yet. Fit one from the factor workbench.
    </p>
    <table
      v-else
      class="w-full text-left text-sm"
    >
      <thead class="border-b border-slate-200 text-slate-500">
        <tr>
          <th class="py-2 pr-4">
            Model
          </th>
          <th class="py-2 pr-4">
            Version
          </th>
          <th class="py-2">
            Status
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="model in models"
          :key="model.id"
          class="border-b border-slate-100"
        >
          <td class="py-3 pr-4">
            <RouterLink
              :to="`/models/${model.model_family_slug}?version=${model.version}`"
              class="font-medium text-sky-700 hover:underline"
            >
              {{ model.model_family_slug }}
            </RouterLink>
          </td>
          <td class="py-3 pr-4">
            {{ model.version }}
          </td>
          <td class="py-3">
            {{ model.status }}
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>
