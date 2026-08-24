<script setup lang="ts">
import { computed } from "vue";
import { RouterLink } from "vue-router";

import { parseModelRef } from "@/api/comparisons";

const props = defineProps<{ modelRef: string; muted?: boolean }>();

// Null on a well-formed artifact, not only on a malformed one — see `parseModelRef`.
const parsed = computed(() => parseModelRef(props.modelRef));
</script>

<template>
  <RouterLink
    v-if="parsed"
    :to="`/models/${parsed.slug}?version=${parsed.version}`"
    class="font-mono text-xs underline decoration-slate-300 underline-offset-2 hover:decoration-slate-900"
    :class="muted ? 'text-slate-500' : 'text-slate-900'"
  >
    {{ parsed.slug }}@{{ parsed.version }}
  </RouterLink>
  <span
    v-else
    class="font-mono text-xs"
    :class="muted ? 'text-slate-500' : 'text-slate-900'"
    title="Not a versioned model reference, so it cannot be resolved to a model page"
  >{{ modelRef }}</span>
</template>
