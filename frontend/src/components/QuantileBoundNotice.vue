<script setup lang="ts">
import { computed } from "vue";
import { RouterLink } from "vue-router";

import { boundCentral, type Model } from "@/api/models";

const props = defineProps<{ model: Model }>();

/**
 * FR-199: a bound is a Model in its own right — same Model Family, dataset version,
 * split and factor set — fitted with the `quantile` template at a declared alpha. Nothing
 * about its coefficients, its metadata or its fit time distinguishes it from the central
 * estimate on screen, so a bound that does not say it is a bound is a model whose
 * predictions read as means.
 */
const bound = computed(() => boundCentral(props.model));

/**
 * The side is read off alpha rather than declared, because the backend declares only the
 * quantile. A bound fitted at 0.95 rendered as "lower" is the one error on this notice that
 * reverses its meaning without looking wrong.
 */
const side = computed(() =>
  bound.value === null ? null : bound.value.alpha < 0.5 ? "lower" : "upper",
);
</script>

<template>
  <aside
    v-if="bound && side"
    class="mt-6 rounded-md border border-slate-200 bg-slate-50 p-4 text-sm"
  >
    <p>
      This model is the <strong>{{ side }} bound</strong> of
      <RouterLink
        :to="{
          name: 'model-detail',
          params: { slug: bound.slug },
          query: { version: String(bound.version) },
        }"
        class="font-mono hover:underline"
      >
        {{ bound.slug }}@{{ bound.version }}
      </RouterLink>, at alpha {{ bound.alpha }}.
    </p>
    <!-- FR-199: a bound is fitted with the `quantile` template and estimates that
         quantile. Its predictions are not this family's central estimate, and a page that
         shows the numbers without saying so invites exactly that reading. -->
    <p class="mt-1 text-slate-600">
      A bound estimates that quantile, not the mean. Read it beside the model it bounds.
    </p>
  </aside>
</template>
