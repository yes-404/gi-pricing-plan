<script setup lang="ts">
/**
 * A GLM approximation's diagnostics are measured against another model's predictions
 * (FR-137, FR-141).
 *
 * A surrogate is a GLM in every visible respect — family, link, coefficients, relativities —
 * so nothing on a page distinguishes one, and its A/E, residuals and lift are read as fit to
 * experience unless the page says otherwise. `GlmSpec` refuses a spec that sets
 * `approximates_model_id` without the surrogate response column, and refuses the converse,
 * so this one field is a sound test for "is a surrogate".
 *
 * No link: the id is not resolvable to a slug from either the model or the diagnostics
 * response, and a route built from a UUID would be a guess.
 */
defineProps<{ approximatesModelId: string | null }>();
</script>

<template>
  <p
    v-if="approximatesModelId"
    role="note"
    class="mt-2 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
  >
    This model is a GLM approximation of model
    <span class="font-mono text-xs">{{ approximatesModelId }}</span>. Its diagnostics are
    measured against that model's predictions, not against observed claims.
  </p>
</template>
